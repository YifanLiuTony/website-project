#!/usr/bin/env python3
"""Create and apply reviewed previews for Parete image email/URL cleanup.

The input inventory divides source images into automatic and manual-review
groups. By default this tool writes cleaned preview copies and an HTML review
gallery without altering source files or public assets. Once the gallery has
been approved, ``--apply-approved`` backs up originals and copies only the
reviewed preview files into parete-scrape/images/.

Pillow performs all image edits. On macOS, Vision OCR is queried through Swift
to keep URL removal tightly bounded. If OCR is unavailable or misses a tagged
URL, a conservative narrow bottom crop is generated and flagged in the review
manifest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import os
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageOps, ImageStat

AUTO_GROUPS = {"easy_footer_crop_or_cover", "bottom_url_mask_candidate"}
FOOTER_GROUP = "easy_footer_crop_or_cover"
BOTTOM_GROUP = "bottom_url_mask_candidate"
MANUAL_GROUP = "manual_review"

VISION_SWIFT = r"""
import Foundation
import Vision

for rawPath in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: rawPath)
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    do {
        try VNImageRequestHandler(url: url, options: [:]).perform([request])
        for observation in request.results ?? [] {
            guard let candidate = observation.topCandidates(1).first else { continue }
            let text = candidate.string.replacingOccurrences(of: "\t", with: " ")
            let lower = text.lowercased()
            let hasBrand = lower.contains("parete")
            let hasURLShape = lower.contains("www") || lower.contains(".ne") ||
                lower.contains(".com") || lower.contains("accessfloor")
            if hasBrand && hasURLShape {
                let box = observation.boundingBox
                let fields: [String] = ["BOX", rawPath, text, String(describing: box.origin.x),
                    String(describing: box.origin.y), String(describing: box.width),
                    String(describing: box.height)]
                print(fields.joined(separator: "\t"))
            }
        }
    } catch {
        let fields: [String] = ["ERROR", rawPath, error.localizedDescription]
        print(fields.joined(separator: "\t"))
    }
}
"""


@dataclass(frozen=True)
class OCRBox:
    text: str
    x: float
    y: float
    width: float
    height: float


def parse_args() -> argparse.Namespace:
    script_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", type=Path, default=script_root)
    parser.add_argument("--input-root", type=Path, help="Read preview inputs from a preserved-originals directory.")
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--footer-crop-pixels", type=int, default=47)
    parser.add_argument("--no-vision", action="store_true", help="Skip macOS Vision OCR and generate flagged fallback crops.")
    parser.add_argument(
        "--manual-review-gallery",
        action="store_true",
        help="Write an original-only gallery for manual-review candidates without altering images.",
    )
    parser.add_argument(
        "--manual-url-preview",
        action="store_true",
        help="Write cleaned previews for selected manual-review URL candidates without altering images.",
    )
    parser.add_argument(
        "--manual-exclude",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="Exclude a confirmed-clean manual-review path from --manual-url-preview. May be repeated.",
    )
    parser.add_argument("--apply-approved", action="store_true", help="Apply an existing reviewed preview manifest to source images.")
    parser.add_argument(
        "--apply-manual-approved",
        action="store_true",
        help="Apply the reviewed manual-preview manifest to source images after backing up originals.",
    )
    parser.add_argument(
        "--allow-caption-overlap",
        action="store_true",
        help="Allow approved URL masks that cover already-overlapped caption text.",
    )
    parser.add_argument(
        "--allow-revised-preview",
        action="store_true",
        help="Allow an already-applied source to be updated from a corrected reviewed-preview output.",
    )
    return parser.parse_args()


def load_inventory(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"relative_source_path", "cleanup_group", "basis", "detected_text"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"Inventory is missing required columns: {path}")
    return rows


def validate_paths(site_root: Path, source_root: Path, output_root: Path) -> None:
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    assets_root = (site_root / "assets" / "products").resolve()
    if output_root == source_root or source_root in output_root.parents:
        raise SystemExit("Output directory must not be within parete-scrape/images/.")
    if output_root == assets_root or assets_root in output_root.parents:
        raise SystemExit("Output directory must not be within assets/products/.")


def collect_vision_boxes(paths: list[Path]) -> tuple[dict[Path, list[OCRBox]], str | None]:
    swift = shutil.which("swift")
    if not swift:
        return {}, "swift not available for Vision OCR"
    boxes: dict[Path, list[OCRBox]] = defaultdict(list)
    errors = []
    batch_size = 24
    module_cache = Path(tempfile.gettempdir()) / "parete-swift-module-cache"
    module_cache.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["CLANG_MODULE_CACHE_PATH"] = str(module_cache)
    environment["SWIFT_MODULECACHE_PATH"] = str(module_cache)
    for start in range(0, len(paths), batch_size):
        batch = paths[start : start + batch_size]
        command = [swift, "-e", VISION_SWIFT, *[str(path.resolve()) for path in batch]]
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, check=False, timeout=300, env=environment
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"batch {start // batch_size + 1}: {exc}")
            continue
        if completed.returncode != 0:
            errors.append(f"batch {start // batch_size + 1}: Swift exited {completed.returncode}")
            continue
        for line in completed.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) != 7 or parts[0] != "BOX":
                continue
            source = Path(parts[1]).resolve()
            try:
                boxes[source].append(
                    OCRBox(parts[2], float(parts[3]), float(parts[4]), float(parts[5]), float(parts[6]))
                )
            except ValueError:
                continue
    note = "Vision OCR batch failures: " + "; ".join(errors) if errors else None
    return dict(boxes), note


def collect_enhanced_corner_boxes(paths: list[Path]) -> tuple[dict[Path, list[OCRBox]], str | None]:
    """Retry faint bottom-right URLs on enlarged contrast variants and map boxes back."""
    variants: list[Path] = []
    mapping: dict[Path, tuple[Path, tuple[int, int, int, int], tuple[int, int]]] = {}
    with tempfile.TemporaryDirectory(prefix="parete-corner-ocr-") as temporary:
        temporary_root = Path(temporary)
        for index, path in enumerate(paths):
            with Image.open(path) as image:
                rgb = on_white(image)
                left = round(rgb.width * 0.45)
                top = round(rgb.height * 0.45)
                crop_box = (left, top, rgb.width, rgb.height)
                corner = rgb.crop(crop_box)
                gray = ImageOps.autocontrast(ImageOps.grayscale(corner))
                candidates = [
                    gray,
                    ImageOps.invert(gray),
                    gray.point(lambda pixel: 255 if pixel > 180 else 0),
                    gray.point(lambda pixel: 255 if pixel > 220 else 0),
                ]
                for variant_index, candidate in enumerate(candidates):
                    variant = temporary_root / f"{index:03d}-{variant_index}.png"
                    candidate.resize(
                        (candidate.width * 4, candidate.height * 4),
                        Image.Resampling.LANCZOS,
                    ).save(variant)
                    variants.append(variant.resolve())
                    mapping[variant.resolve()] = (path.resolve(), crop_box, rgb.size)
        detected, note = collect_vision_boxes(variants)
        mapped: dict[Path, list[OCRBox]] = defaultdict(list)
        for variant, boxes in detected.items():
            source, crop_box, dimensions = mapping[variant]
            left, top, right, bottom = crop_box
            width, height = dimensions
            crop_width = right - left
            crop_height = bottom - top
            for box in boxes:
                mapped[source].append(
                    OCRBox(
                        box.text,
                        (left + box.x * crop_width) / width,
                        (height - bottom + box.y * crop_height) / height,
                        box.width * crop_width / width,
                        box.height * crop_height / height,
                    )
                )
        selected: dict[Path, list[OCRBox]] = {}
        for source, boxes in mapped.items():
            url_only = [box for box in boxes if not has_caption_prefix(box.text)]
            chosen = max(url_only or boxes, key=lambda box: box.width)
            selected[source] = [chosen]
        return selected, note


def on_white(image: Image.Image) -> Image.Image:
    if image.mode == "RGBA":
        flattened = Image.new("RGBA", image.size, (255, 255, 255, 255))
        flattened.alpha_composite(image)
        return flattened.convert("RGB")
    return image.convert("RGB")


def lower_band_luminance(image: Image.Image) -> float:
    rgb = on_white(image)
    top = int(rgb.height * 0.80)
    return ImageStat.Stat(rgb.crop((0, top, rgb.width, rgb.height)).convert("L")).mean[0]


def is_diagram_like(image: Image.Image, detected_text: str, boxes: list[OCRBox]) -> bool:
    texts = " ".join([detected_text, *[box.text for box in boxes]]).lower()
    if "accessfloor" in texts:
        return True
    if any(has_caption_prefix(box.text) for box in boxes):
        return True
    return lower_band_luminance(image) >= 218


def pixel_box(image: Image.Image, box: OCRBox, tight: bool = False) -> tuple[int, int, int, int]:
    pad_x = 1 if tight else max(3, round(image.width * 0.004))
    pad_y = 1 if tight else max(2, round(image.height * 0.004))
    left = max(0, math.floor(box.x * image.width) - pad_x)
    top = max(0, math.floor((1 - box.y - box.height) * image.height) - pad_y)
    right = min(image.width, math.ceil((box.x + box.width) * image.width) + pad_x)
    bottom = min(image.height, math.ceil((1 - box.y) * image.height) + pad_y)
    return left, top, right, bottom


def has_caption_prefix(text: str) -> bool:
    lower = text.lower()
    url_start = lower.find("www")
    if url_start < 0:
        parete_start = lower.find("parete")
        url_start = parete_start - 5 if parete_start >= 5 else 0
    return url_start > 5


def only_url_suffix(box: OCRBox) -> OCRBox:
    """Narrow a combined caption/URL OCR line to the visible URL suffix."""
    text = box.text.lower()
    url_start = text.find("www")
    if url_start < 0:
        parete_start = text.find("parete")
        if parete_start >= 0 and "ww" in text[max(0, parete_start - 10) : parete_start]:
            url_start = max(0, parete_start - 12)
        else:
            url_start = max(0, parete_start - 5) if parete_start >= 0 else 0
    if url_start <= 0 or len(text) == 0:
        return box
    start_ratio = max(0.0, (url_start / len(text)) - 0.045)
    shifted_x = box.x + (box.width * start_ratio)
    return OCRBox(box.text, shifted_x, box.y, box.width * (1 - start_ratio), box.height)


def white_fill(image: Image.Image) -> tuple[int, ...]:
    return (255, 255, 255, 255) if "A" in image.mode else (255, 255, 255)


def mask_diagram_urls(image: Image.Image, boxes: list[OCRBox]) -> tuple[Image.Image, str]:
    cleaned = image.copy()
    fill = white_fill(cleaned)
    areas = []
    for box in boxes:
        area = pixel_box(cleaned, only_url_suffix(box), tight=True)
        areas.append(area)
        patch = Image.new(cleaned.mode, (area[2] - area[0], area[3] - area[1]), fill)
        cleaned.paste(patch, (area[0], area[1]))
    detail = "; ".join(f"{box.text} at {area}" for box, area in zip(boxes, areas))
    return cleaned, detail


def crop_detected_bottom_url(image: Image.Image, boxes: list[OCRBox]) -> tuple[Image.Image, str]:
    relevant = [box for box in boxes if box.y < 0.20]
    if not relevant:
        return fallback_bottom_crop(image)
    upper_url_edge = min(pixel_box(image, box)[1] for box in relevant)
    crop_y = max(round(image.height * 0.78), upper_url_edge)
    return image.crop((0, 0, image.width, crop_y)), f"cropped at y={crop_y} from detected bottom URL"


def crop_email_footer(image: Image.Image, boxes: list[OCRBox], default_pixels: int) -> tuple[Image.Image, str]:
    crop_y = image.height - min(default_pixels, image.height - 1)
    retained_boxes = [box for box in boxes if pixel_box(image, box)[1] < crop_y]
    if retained_boxes:
        text_top = min(pixel_box(image, box)[1] for box in retained_boxes)
        crop_y = max(round(image.height * 0.60), text_top - max(10, round(image.height * 0.025)))
        return image.crop((0, 0, image.width, crop_y)), f"cropped detected removable bottom footer at y={crop_y}"
    return image.crop((0, 0, image.width, crop_y)), f"cropped removable bottom footer ({default_pixels}px)"


def fallback_bottom_crop(image: Image.Image) -> tuple[Image.Image, str]:
    pixels = min(42, max(14, round(image.height * 0.10)))
    crop_y = image.height - pixels
    return image.crop((0, 0, image.width, crop_y)), f"fallback crop of bottom {pixels}px; verify URL removal"


def mask_fallback_bottom_right_url(image: Image.Image) -> tuple[Image.Image, str]:
    cleaned = image.copy()
    mask_width = min(cleaned.width, max(180, round(cleaned.width * 0.28)))
    mask_height = min(cleaned.height, max(30, min(48, round(cleaned.height * 0.12))))
    area = (cleaned.width - mask_width, cleaned.height - mask_height, cleaned.width, cleaned.height)
    patch = Image.new(cleaned.mode, (mask_width, mask_height), white_fill(cleaned))
    cleaned.paste(patch, (area[0], area[1]))
    return cleaned, f"masked bottom-right corner at {area}; verify any overlapping caption text"


def save_image(image: Image.Image, destination: Path, source_format: str | None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image_format = source_format or ("PNG" if destination.suffix.lower() == ".png" else "JPEG")
    if image_format.upper() in {"JPEG", "JPG"}:
        image.convert("RGB").save(destination, format="JPEG", quality=95, subsampling=0, optimize=True)
    else:
        image.save(destination, format=image_format)


def relative_url(path: str) -> str:
    return quote(path.replace("\\", "/"), safe="/-_.()")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_preview_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"relative_source_path", "cleanup_group", "action", "preview_relative_path"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"Preview manifest is missing required columns: {path}")
    return rows


def write_manifest(path: Path, results: list[dict[str, str]]) -> None:
    fields = [
        "relative_source_path",
        "cleanup_group",
        "action",
        "detail",
        "ocr_text",
        "original_dimensions",
        "preview_dimensions",
        "preview_relative_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def write_gallery(
    path: Path,
    output_root: Path,
    results: list[dict[str, str]],
    inventory_counts: Counter[str],
    action_counts: Counter[str],
    vision_note: str | None,
    before_prefix: str = "../images/",
    applied: bool = False,
    heading: str = "Parete Image Email/URL Cleanup Preview",
    count_text: str | None = None,
) -> None:
    cards = []
    for item in results:
        source_url = relative_url(before_prefix + item["relative_source_path"])
        preview_url = relative_url(item["preview_relative_path"])
        label = html.escape(item["relative_source_path"])
        action = html.escape(item["action"])
        detail = html.escape(item["detail"])
        group = html.escape(item["cleanup_group"])
        cards.append(
            f"""<article class="card" data-group="{group}" data-action="{action}">
  <h3>{label}</h3>
  <p class="meta"><strong>{group}</strong> | {action}<br>{detail}</p>
  <div class="pair">
    <figure><img loading="lazy" src="{source_url}" alt="Original {label}"><figcaption>Before</figcaption></figure>
    <figure><img loading="lazy" src="{preview_url}" alt="Preview {label}"><figcaption>Preview</figcaption></figure>
  </div>
</article>"""
        )
    vision_html = f"<p class=\"notice\">{html.escape(vision_note)}</p>" if vision_note else ""
    summary = " ".join(
        f"<span><b>{html.escape(name)}</b>: {count}</span>" for name, count in sorted(action_counts.items())
    )
    status_text = (
        "Applied output: before images are preserved originals; preview images are the approved source replacements."
        if applied
        else "Review-only output: source images and generated public assets have not been replaced."
    )
    count_text = count_text or (
        f"Processed {len(results)} candidates; left unchanged for manual review: {inventory_counts[MANUAL_GROUP]}."
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(heading)}</title>
<style>
  :root {{ color-scheme: light; --ink: #18222c; --line: #d8dde3; --accent: #155b85; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 14px/1.45 Arial, sans-serif; color: var(--ink); background: #f3f5f7; }}
  header {{ position: sticky; top: 0; z-index: 2; padding: 18px 24px 14px; background: #fff; border-bottom: 1px solid var(--line); }}
  h1 {{ margin: 0 0 6px; font-size: 23px; }}
  header p {{ margin: 4px 0; }}
  .counts {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }}
  .counts span {{ padding: 5px 9px; border-radius: 16px; background: #eaf1f5; }}
  .notice {{ color: #804a08; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(470px, 1fr)); gap: 15px; padding: 18px; }}
  .card {{ padding: 12px; overflow: hidden; background: #fff; border: 1px solid var(--line); border-radius: 8px; }}
  h3 {{ margin: 0 0 6px; font-size: 13px; overflow-wrap: anywhere; }}
  .meta {{ min-height: 40px; margin: 0 0 9px; color: #4b5965; font-size: 12px; }}
  .meta strong {{ color: var(--accent); }}
  .pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  figure {{ margin: 0; }}
  img {{ display: block; width: 100%; height: 240px; object-fit: contain; background: #eef1f3; border: 1px solid var(--line); }}
  figcaption {{ margin-top: 4px; color: #536371; font-weight: bold; }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(heading)}</h1>
  <p>{status_text}</p>
  <p>{html.escape(count_text)}</p>
  <div class="counts">{summary}</div>
  {vision_html}
</header>
<main>
{''.join(cards)}
</main>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")


def write_manual_gallery(
    path: Path,
    rows: list[dict[str, str]],
    boxes_by_path: dict[Path, list[OCRBox]],
    source_root: Path,
    vision_note: str | None,
) -> int:
    cards = []
    ocr_flagged = 0
    for row in rows:
        relative_path = row["relative_source_path"]
        boxes = boxes_by_path.get((source_root / relative_path).resolve(), [])
        ocr_text = "; ".join(box.text for box in boxes)
        if boxes:
            ocr_flagged += 1
            status_class = "flagged"
            status = "OCR found likely URL text"
            details = html.escape(ocr_text)
        else:
            status_class = "inspect"
            status = "Inspect visually"
            details = "No URL/email text confirmed by OCR rescan"
        source_url = relative_url("../images/" + relative_path)
        label = html.escape(relative_path)
        cards.append(
            f"""<article class="card {status_class}" data-status="{status_class}">
  <h3>{label}</h3>
  <p class="meta"><strong>{status}</strong><br>{details}</p>
  <a href="{source_url}" target="_blank"><img loading="lazy" src="{source_url}" alt="Manual review {label}"></a>
</article>"""
        )
    note_html = f'<p class="notice">{html.escape(vision_note)}</p>' if vision_note else ""
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parete Manual Image URL Review</title>
<style>
  :root {{ color-scheme: light; --ink: #18222c; --line: #d8dde3; --accent: #155b85; --flag: #a43a25; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 14px/1.45 Arial, sans-serif; color: var(--ink); background: #f3f5f7; }}
  header {{ position: sticky; top: 0; z-index: 2; padding: 18px 24px 14px; background: #fff; border-bottom: 1px solid var(--line); }}
  h1 {{ margin: 0 0 6px; font-size: 23px; }}
  header p {{ margin: 4px 0; }}
  nav {{ display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 12px; }}
  nav a, button {{ padding: 6px 11px; color: var(--accent); background: #eaf1f5; border: 0; border-radius: 16px; cursor: pointer; text-decoration: none; }}
  button.active {{ background: var(--accent); color: #fff; }}
  .notice {{ color: #804a08; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 15px; padding: 18px; }}
  .card {{ padding: 12px; overflow: hidden; background: #fff; border: 1px solid var(--line); border-radius: 8px; }}
  .card.flagged {{ border-color: #e5a394; }}
  h3 {{ margin: 0 0 6px; font-size: 13px; overflow-wrap: anywhere; }}
  .meta {{ min-height: 42px; margin: 0 0 9px; color: #4b5965; font-size: 12px; }}
  .meta strong {{ color: var(--accent); }}
  .flagged .meta strong {{ color: var(--flag); }}
  img {{ display: block; width: 100%; height: 300px; object-fit: contain; background: #eef1f3; border: 1px solid var(--line); }}
</style>
</head>
<body>
<header>
  <h1>Parete Manual Review Candidates</h1>
  <p>Original source images only. No image in this manual-review group has been altered.</p>
  <p>{len(rows)} images require visual judgment; OCR rescan flagged {ocr_flagged} likely URL marks. Faint visible marks may not be detected by OCR.</p>
  {note_html}
  <nav>
    <a href="gallery.html">Processed before/after gallery</a>
    <button class="active" type="button" onclick="filterCards('all', this)">All {len(rows)}</button>
    <button type="button" onclick="filterCards('flagged', this)">OCR flagged {ocr_flagged}</button>
    <button type="button" onclick="filterCards('inspect', this)">Visual check {len(rows) - ocr_flagged}</button>
  </nav>
</header>
<main>
{''.join(cards)}
</main>
<script>
function filterCards(status, button) {{
  document.querySelectorAll('button').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {{
    card.hidden = status !== 'all' && card.dataset.status !== status;
  }});
}}
</script>
</body>
</html>
"""
    path.write_text(html_text, encoding="utf-8")
    return ocr_flagged


def apply_approved_previews(
    source_root: Path,
    output_root: Path,
    inventory_rows: list[dict[str, str]],
    results: list[dict[str, str]],
    allow_caption_overlap: bool,
    allow_revised_preview: bool,
) -> Path:
    expected_paths = {
        row["relative_source_path"] for row in inventory_rows if row["cleanup_group"] in AUTO_GROUPS
    }
    manifest_paths = {row["relative_source_path"] for row in results}
    if manifest_paths != expected_paths:
        missing = sorted(expected_paths - manifest_paths)
        extra = sorted(manifest_paths - expected_paths)
        raise SystemExit(f"Approved manifest does not match automatic inventory rows: missing={missing[:3]} extra={extra[:3]}")
    flagged = [row["relative_source_path"] for row in results if row["action"] == "mask_url_over_caption_review"]
    if flagged and not allow_caption_overlap:
        raise SystemExit("Approved manifest includes caption-overlap masks; pass --allow-caption-overlap after approval.")

    backup_root = output_root / "originals"
    for row in results:
        source = source_root / row["relative_source_path"]
        preview = output_root / row["preview_relative_path"]
        backup = backup_root / row["relative_source_path"]
        if not source.is_file() or not preview.is_file():
            raise SystemExit(f"Missing source or preview file for {row['relative_source_path']}")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(source, backup)
        elif sha256(source) not in {sha256(backup), sha256(preview)} and not allow_revised_preview:
            raise SystemExit(f"Source has changed outside the approved apply flow: {row['relative_source_path']}")

    for row in results:
        source = source_root / row["relative_source_path"]
        preview = output_root / row["preview_relative_path"]
        shutil.copy2(preview, source)
        if sha256(source) != sha256(preview):
            raise SystemExit(f"Source replacement verification failed: {row['relative_source_path']}")
    return backup_root


def apply_manual_approved_previews(
    source_root: Path,
    output_root: Path,
    inventory_rows: list[dict[str, str]],
    results: list[dict[str, str]],
    preview_summary: dict[str, object],
    allow_caption_overlap: bool,
    allow_revised_preview: bool,
) -> Path:
    manual_paths = {
        row["relative_source_path"] for row in inventory_rows if row["cleanup_group"] == MANUAL_GROUP
    }
    excluded = set(preview_summary.get("manual_confirmed_clean_excluded", []))
    ignored = set(preview_summary.get("manual_broken_retrieval_ignored", []))
    expected_paths = manual_paths - excluded - ignored
    manifest_paths = {row["relative_source_path"] for row in results}
    if manifest_paths != expected_paths:
        missing = sorted(expected_paths - manifest_paths)
        extra = sorted(manifest_paths - expected_paths)
        raise SystemExit(f"Manual manifest does not match reviewed candidate set: missing={missing[:3]} extra={extra[:3]}")
    if not all(row["preview_relative_path"].startswith("manual-processed/") for row in results):
        raise SystemExit("Manual manifest includes a preview outside manual-processed/.")
    flagged = [row["relative_source_path"] for row in results if row["action"] == "mask_url_over_caption_review"]
    if flagged and not allow_caption_overlap:
        raise SystemExit("Manual manifest includes caption-overlap masks; pass --allow-caption-overlap after approval.")

    backup_root = output_root / "manual-originals"
    for row in results:
        source = source_root / row["relative_source_path"]
        preview = output_root / row["preview_relative_path"]
        backup = backup_root / row["relative_source_path"]
        if not source.is_file() or not preview.is_file():
            raise SystemExit(f"Missing manual source or preview file for {row['relative_source_path']}")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(source, backup)
        elif sha256(source) not in {sha256(backup), sha256(preview)} and not allow_revised_preview:
            raise SystemExit(f"Manual source has changed outside the approved apply flow: {row['relative_source_path']}")

    for row in results:
        source = source_root / row["relative_source_path"]
        preview = output_root / row["preview_relative_path"]
        shutil.copy2(preview, source)
        if sha256(source) != sha256(preview):
            raise SystemExit(f"Manual source replacement verification failed: {row['relative_source_path']}")
    return backup_root


def main() -> None:
    args = parse_args()
    site_root = args.site_root.resolve()
    source_root = site_root / "parete-scrape" / "images"
    input_root = (args.input_root or source_root).resolve()
    inventory = (args.inventory or site_root / "parete-scrape" / "image-url-branding-inventory.csv").resolve()
    output_root = (args.output_dir or site_root / "parete-scrape" / "image-url-cleanup-preview-2026-05-26").resolve()
    processed_root = output_root / "processed"
    validate_paths(site_root, source_root, output_root)

    rows = load_inventory(inventory)
    counts = Counter(row["cleanup_group"] for row in rows)
    missing = [
        row["relative_source_path"]
        for row in rows
        if row["cleanup_group"] in AUTO_GROUPS and not (input_root / row["relative_source_path"]).is_file()
    ]
    if missing:
        raise SystemExit(f"Inventory references missing source files ({len(missing)}): {missing[0]}")

    if args.manual_review_gallery:
        manual_rows = [row for row in rows if row["cleanup_group"] == MANUAL_GROUP]
        manual_paths = [(source_root / row["relative_source_path"]).resolve() for row in manual_rows]
        missing_manual = [str(path) for path in manual_paths if not path.is_file()]
        if missing_manual:
            raise SystemExit(f"Inventory references missing manual-review files ({len(missing_manual)}): {missing_manual[0]}")
        if args.no_vision:
            manual_boxes = {}
            manual_note = "Vision OCR disabled; inspect all manual-review images visually."
        else:
            manual_boxes, manual_note = collect_vision_boxes(manual_paths)
        output_root.mkdir(parents=True, exist_ok=True)
        manual_gallery_path = output_root / "manual-review.html"
        ocr_flagged = write_manual_gallery(manual_gallery_path, manual_rows, manual_boxes, source_root, manual_note)
        print(f"Manual review gallery: {manual_gallery_path}")
        print(f"Manual candidates: {len(manual_rows)}; OCR flagged: {ocr_flagged}")
        return

    if args.manual_url_preview:
        excluded = set(args.manual_exclude)
        manual_rows = [row for row in rows if row["cleanup_group"] == MANUAL_GROUP]
        manual_paths = {row["relative_source_path"] for row in manual_rows}
        unknown_exclusions = sorted(excluded - manual_paths)
        if unknown_exclusions:
            raise SystemExit(f"Manual exclusions are not manual-review inventory paths: {unknown_exclusions[0]}")
        broken_rows = [row for row in manual_rows if "__" in Path(row["relative_source_path"]).name]
        candidate_rows = [
            row
            for row in manual_rows
            if row["relative_source_path"] not in excluded
            and "__" not in Path(row["relative_source_path"]).name
        ]
        candidate_paths = [(source_root / row["relative_source_path"]).resolve() for row in candidate_rows]
        missing_manual = [str(path) for path in candidate_paths if not path.is_file()]
        if missing_manual:
            raise SystemExit(f"Inventory references missing manual URL candidate files ({len(missing_manual)}): {missing_manual[0]}")
        if args.no_vision:
            manual_boxes = {}
            manual_note = "Vision OCR disabled; all previews require visual confirmation."
        else:
            manual_boxes, manual_note = collect_vision_boxes(candidate_paths)
            remaining_paths = [path for path in candidate_paths if path not in manual_boxes]
            enhanced_boxes, enhanced_note = collect_enhanced_corner_boxes(remaining_paths)
            manual_boxes.update(enhanced_boxes)
            notes = [note for note in [manual_note, enhanced_note] if note]
            manual_note = "; ".join(notes) or None
        results: list[dict[str, str]] = []
        action_counts: Counter[str] = Counter()
        manual_processed_root = output_root / "manual-processed"
        for row in candidate_rows:
            relative_path = row["relative_source_path"]
            source = source_root / relative_path
            destination = manual_processed_root / relative_path
            with Image.open(source) as image:
                original_dimensions = f"{image.width}x{image.height}"
                boxes = manual_boxes.get(source.resolve(), [])
                has_overlapping_caption = any(has_caption_prefix(box.text) for box in boxes)
                is_pale_png_diagram = source.suffix.lower() == ".png" and lower_band_luminance(image) >= 218
                if boxes and (has_overlapping_caption or is_pale_png_diagram):
                    cleaned, detail = mask_diagram_urls(image, boxes)
                    action = "mask_detected_url_boxes"
                    if has_overlapping_caption:
                        action = "mask_url_over_caption_review"
                        detail = "URL overlaps adjacent caption; review covered text. " + detail
                elif boxes:
                    cleaned, detail = crop_detected_bottom_url(image, boxes)
                    action = "crop_detected_bottom_url"
                elif is_diagram_like(image, row["detected_text"], boxes):
                    cleaned, detail = mask_fallback_bottom_right_url(image)
                    action = "mask_bottom_right_url_review"
                else:
                    cleaned, detail = fallback_bottom_crop(image)
                    action = "fallback_bottom_crop_review"
                preview_dimensions = f"{cleaned.width}x{cleaned.height}"
                save_image(cleaned, destination, image.format)
            action_counts[action] += 1
            results.append(
                {
                    "relative_source_path": relative_path,
                    "cleanup_group": MANUAL_GROUP,
                    "action": action,
                    "detail": detail,
                    "ocr_text": "; ".join(box.text for box in boxes),
                    "original_dimensions": original_dimensions,
                    "preview_dimensions": preview_dimensions,
                    "preview_relative_path": str(destination.relative_to(output_root)),
                }
            )
        output_root.mkdir(parents=True, exist_ok=True)
        manifest_path = output_root / "manual-preview-manifest.csv"
        gallery_path = output_root / "manual-cleanup-gallery.html"
        write_manifest(manifest_path, results)
        write_gallery(
            gallery_path,
            output_root,
            results,
            counts,
            action_counts,
            manual_note,
            heading="Parete Manual URL Cleanup Preview",
            count_text=(
                f"Generated {len(results)} manual candidate previews; excluded confirmed-clean: "
                f"{len(excluded)}; ignored broken retrieval files: {len(broken_rows)}."
            ),
        )
        summary = {
            "source_root": str(source_root),
            "inventory": str(inventory),
            "output_root": str(output_root),
            "manual_candidate_previews": len(results),
            "manual_confirmed_clean_excluded": sorted(excluded),
            "manual_broken_retrieval_ignored": [row["relative_source_path"] for row in broken_rows],
            "action_counts": dict(action_counts),
            "vision_note": manual_note,
            "source_or_public_assets_replaced": False,
        }
        (output_root / "manual-preview-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        print(f"Manual cleanup gallery: {gallery_path}")
        return

    if args.apply_approved:
        manifest_path = output_root / "preview-manifest.csv"
        results = load_preview_manifest(manifest_path)
        action_counts = Counter(row["action"] for row in results)
        backup_root = apply_approved_previews(
            source_root,
            output_root,
            rows,
            results,
            allow_caption_overlap=args.allow_caption_overlap,
            allow_revised_preview=args.allow_revised_preview,
        )
        gallery_path = output_root / "gallery.html"
        summary_path = output_root / "summary.json"
        write_gallery(
            gallery_path,
            output_root,
            results,
            counts,
            action_counts,
            None,
            before_prefix="originals/",
            applied=True,
        )
        summary = {
            "source_root": str(source_root),
            "inventory": str(inventory),
            "output_root": str(output_root),
            "backup_root": str(backup_root),
            "inventory_counts": dict(counts),
            "processed_count": len(results),
            "action_counts": dict(action_counts),
            "manual_review_unchanged": counts[MANUAL_GROUP],
            "source_images_replaced": True,
            "public_assets_regenerated": False,
        }
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        print(f"Applied gallery: {gallery_path}")
        return

    if args.apply_manual_approved:
        manifest_path = output_root / "manual-preview-manifest.csv"
        preview_summary_path = output_root / "manual-preview-summary.json"
        results = load_preview_manifest(manifest_path)
        preview_summary = json.loads(preview_summary_path.read_text(encoding="utf-8"))
        action_counts = Counter(row["action"] for row in results)
        backup_root = apply_manual_approved_previews(
            source_root,
            output_root,
            rows,
            results,
            preview_summary,
            allow_caption_overlap=args.allow_caption_overlap,
            allow_revised_preview=args.allow_revised_preview,
        )
        gallery_path = output_root / "manual-cleanup-gallery.html"
        write_gallery(
            gallery_path,
            output_root,
            results,
            counts,
            action_counts,
            None,
            before_prefix="manual-originals/",
            applied=True,
            heading="Parete Manual URL Cleanup Preview",
            count_text=(
                f"Applied {len(results)} approved manual candidate previews; excluded confirmed-clean: "
                f"{len(preview_summary['manual_confirmed_clean_excluded'])}; ignored broken retrieval files: "
                f"{len(preview_summary['manual_broken_retrieval_ignored'])}."
            ),
        )
        preview_summary.update(
            {
                "manual_backup_root": str(backup_root),
                "source_images_replaced": True,
                "public_assets_regenerated": False,
            }
        )
        preview_summary.pop("source_or_public_assets_replaced", None)
        preview_summary_path.write_text(json.dumps(preview_summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(preview_summary, indent=2))
        print(f"Applied manual gallery: {gallery_path}")
        return

    auto_paths = [
        (input_root / row["relative_source_path"]).resolve()
        for row in rows
        if row["cleanup_group"] in AUTO_GROUPS
    ]
    boxes_by_path: dict[Path, list[OCRBox]] = {}
    vision_note = None
    if args.no_vision:
        vision_note = "Vision OCR disabled; all bottom URL candidates use flagged fallback crops."
    else:
        boxes_by_path, vision_note = collect_vision_boxes(auto_paths)

    results: list[dict[str, str]] = []
    action_counts: Counter[str] = Counter()
    for row in rows:
        group = row["cleanup_group"]
        if group not in AUTO_GROUPS:
            continue
        relative_path = row["relative_source_path"]
        source = input_root / relative_path
        destination = processed_root / relative_path
        with Image.open(source) as image:
            original_dimensions = f"{image.width}x{image.height}"
            boxes = boxes_by_path.get(source.resolve(), [])
            if group == FOOTER_GROUP:
                cleaned, detail = crop_email_footer(image, boxes, args.footer_crop_pixels)
                action = "crop_email_footer"
            elif boxes and is_diagram_like(image, row["detected_text"], boxes):
                cleaned, detail = mask_diagram_urls(image, boxes)
                if any(has_caption_prefix(box.text) for box in boxes):
                    action = "mask_url_over_caption_review"
                    detail = "URL overlaps adjacent caption; review covered text. " + detail
                else:
                    action = "mask_detected_url_boxes"
            elif boxes:
                cleaned, detail = crop_detected_bottom_url(image, boxes)
                action = "crop_detected_bottom_url"
            else:
                cleaned, detail = fallback_bottom_crop(image)
                action = "fallback_bottom_crop_review"
            preview_dimensions = f"{cleaned.width}x{cleaned.height}"
            save_image(cleaned, destination, image.format)
        action_counts[action] += 1
        results.append(
            {
                "relative_source_path": relative_path,
                "cleanup_group": group,
                "action": action,
                "detail": detail,
                "ocr_text": "; ".join(box.text for box in boxes),
                "original_dimensions": original_dimensions,
                "preview_dimensions": preview_dimensions,
                "preview_relative_path": str(destination.relative_to(output_root)),
            }
        )

    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "preview-manifest.csv"
    gallery_path = output_root / "gallery.html"
    summary_path = output_root / "summary.json"
    write_manifest(manifest_path, results)
    write_gallery(gallery_path, output_root, results, counts, action_counts, vision_note)
    summary = {
        "source_root": str(source_root),
        "inventory": str(inventory),
        "output_root": str(output_root),
        "inventory_counts": dict(counts),
        "processed_count": len(results),
        "action_counts": dict(action_counts),
        "manual_review_unchanged": counts[MANUAL_GROUP],
        "vision_note": vision_note,
        "source_or_public_assets_replaced": False,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Gallery: {gallery_path}")


if __name__ == "__main__":
    main()
