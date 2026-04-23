#!/usr/bin/env python3
"""Fetch one Parete product page and update the local scrape bundle.

This is intentionally small and product-page focused. It verifies/downloads:
  - EN and ZH gallery images
  - description/body images
  - raw summary/specification/download fields

The Parete ZH pages often reuse English body copy. When an existing local ZH
description is already normalized/translated, this tool preserves that text and
only refreshes image references.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE_URL = "https://www.parete.net/"
UA = "Mozilla/5.0 (compatible; SunflyProductFetcher/1.0)"


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as res:
        raw = res.read()
    # Parete pages are UTF-8 today, but be forgiving.
    return raw.decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as res:
        return res.read()


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def attrs(tag: str) -> dict[str, str]:
    return dict(re.findall(r'([a-zA-Z_:-][a-zA-Z0-9_:-]*)\s*=\s*"([^"]*)"', tag))


def abs_url(src: str, page_url: str) -> str:
    return urljoin(page_url, src)


def local_image_path_for_url(url: str, product_slug: str, existing_map: dict[str, str], body: bool) -> str:
    if url in existing_map:
        return existing_map[url]
    path = urlparse(url).path
    name = Path(path).name
    if body:
        safe = safe_body_name(name)
        return f"images/shared/{safe}"
    return f"images/{product_slug}/{name}"


def safe_body_name(name: str) -> str:
    stem = Path(name).stem
    suffix = Path(name).suffix
    norm = unicodedata.normalize("NFKD", stem)
    norm = "".join(ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "_" for ch in norm)
    norm = re.sub(r"_+", "_", norm).strip("_") or "image"
    return f"images_{norm}{suffix.lower()}"


def download_image(url: str, local_rel: str, scrape_root: Path) -> bool:
    target = scrape_root / local_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        return False
    target.write_bytes(fetch_bytes(url))
    return True


def existing_original_map(product: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for gallery in product.get("gallery", {}).values():
        for item in gallery:
            if item.get("original_url") and item.get("path"):
                out.setdefault(item["original_url"], item["path"])
    for desc in product.get("description", {}).values():
        for tag in re.findall(r"<img\b[^>]*>", desc.get("html", ""), flags=re.I):
            a = attrs(tag)
            orig = a.get("data-original-src")
            src = a.get("src")
            if orig and src:
                out.setdefault(orig, src)
    return out


def extract_gallery(page_html: str, page_url: str, product_slug: str, existing_map: dict[str, str]) -> list[dict]:
    project = re.search(r"<!-- begin project media -->(.*?)<!-- end project media -->", page_html, flags=re.S | re.I)
    if not project:
        return []
    out = []
    for m in re.finditer(r'<a\b[^>]*class="[^"]*fancybox[^"]*"[^>]*>.*?</a>', project.group(1), flags=re.S | re.I):
        a = attrs(m.group(0))
        img_tag = re.search(r"<img\b[^>]*>", m.group(0), flags=re.S | re.I)
        img_attrs = attrs(img_tag.group(0)) if img_tag else {}
        original = abs_url(a.get("href") or img_attrs.get("src", ""), page_url)
        if not original:
            continue
        out.append({
            "path": local_image_path_for_url(original, product_slug, existing_map, body=False),
            "alt": img_attrs.get("alt", a.get("title", "")),
            "caption": a.get("title", img_attrs.get("alt", "")),
            "original_url": original,
        })
    return out


def extract_summary_html(page_html: str) -> str:
    m = re.search(r'<h1 class="producttitle">.*?</h1>(.*?)(?:<br\s*/?>\s*)?<form\b', page_html, flags=re.S | re.I)
    return m.group(1).strip() if m else ""


def extract_summary(page_html: str) -> dict[str, str]:
    summary_html = extract_summary_html(page_html)
    text = strip_tags(summary_html)
    labels = [
        "Brand Name", "Product No.", "MOQ", "Unit Price", "Packing",
        "Packing Style", "Production time", "Delivery time", "Payment terms",
        "Supply Ability",
    ]
    out: dict[str, str] = {}
    for i, label in enumerate(labels):
        next_labels = labels[i + 1:]
        if next_labels:
            pattern = re.escape(label) + r"\s*:?\s*(.*?)(?=" + "|".join(re.escape(x) for x in next_labels) + r"|$)"
        else:
            pattern = re.escape(label) + r"\s*:?\s*(.*)$"
        m = re.search(pattern, text, flags=re.S)
        if m:
            out[label] = re.sub(r"\s+", " ", m.group(1)).strip(" :")
    return out


def extract_specs(page_html: str) -> list[dict[str, str]]:
    m = re.search(r'<div id="tab-2"[^>]*>(.*?)</div>', page_html, flags=re.S | re.I)
    if not m:
        return []
    specs = []
    for li in re.findall(r"<li\b[^>]*>(.*?)</li>", m.group(1), flags=re.S | re.I):
        label_m = re.search(r"<span\b[^>]*>(.*?)</span>", li, flags=re.S | re.I)
        if not label_m:
            continue
        label = strip_tags(label_m.group(1))
        value = strip_tags(re.sub(r"<span\b[^>]*>.*?</span>", "", li, flags=re.S | re.I))
        if label or value:
            specs.append({"label": label, "value": value})
    return specs


def extract_downloads(page_html: str, page_url: str) -> list[dict[str, str]]:
    downloads = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]*attachment[^"]*)"[^>]*>(.*?)</a>', page_html, flags=re.S | re.I):
        label = strip_tags(m.group(2))
        url = abs_url(html.unescape(m.group(1)), page_url)
        downloads.append({"label": label, "url": url})
    return downloads


def extract_description_html(page_html: str) -> str:
    m = re.search(r'<div id="tab-1"[^>]*>(.*?)</div>\s*<div id="tab-2"', page_html, flags=re.S | re.I)
    return m.group(1).strip() if m else ""


def rewrite_description_images(desc_html: str, page_url: str, product_slug: str, existing_map: dict[str, str], scrape_root: Path) -> tuple[str, int, int]:
    downloaded = 0
    seen = 0

    def repl(match: re.Match) -> str:
        nonlocal downloaded, seen
        tag = match.group(0)
        a = attrs(tag)
        src = a.get("src")
        if not src:
            return tag
        original = a.get("data-original-src") or abs_url(src, page_url)
        local_rel = local_image_path_for_url(original, product_slug, existing_map, body=True)
        if download_image(original, local_rel, scrape_root):
            downloaded += 1
        seen += 1
        if "data-original-src" not in a:
            tag = tag[:-2] + f' data-original-src="{html.escape(original, quote=True)}" />' if tag.endswith("/>") else tag[:-1] + f' data-original-src="{html.escape(original, quote=True)}">'
        return re.sub(r'\bsrc="[^"]*"', f'src="{html.escape(local_rel, quote=True)}"', tag, count=1)

    return re.sub(r"<img\b[^>]*>", repl, desc_html, flags=re.I), seen, downloaded


def find_product(data: dict, product_id: str | None, slug: str | None) -> dict:
    for category in data.get("categories", {}).values():
        for product in category.get("products", []):
            if product_id and str(product.get("id")) == str(product_id):
                return product
            if slug and product.get("slug") == slug:
                return product
    raise SystemExit(f"Product not found: id={product_id!r} slug={slug!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--product-id")
    ap.add_argument("--slug")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    site_root = Path(args.site_root).resolve()
    scrape_root = site_root / "parete-scrape"
    products_json = scrape_root / "products.json"
    data = json.loads(products_json.read_text(encoding="utf-8"))
    product = find_product(data, args.product_id, args.slug)
    product_slug = product["slug"]
    existing_map = existing_original_map(product)

    stats = {"gallery": {}, "body_images": {}, "downloaded": 0, "preserved_zh_description": False}
    pages = {
        "en": product["source_url"]["en"],
        "zh": product["source_url"]["zh"],
    }
    fetched = {lang: fetch_text(url) for lang, url in pages.items()}

    for lang, page_html in fetched.items():
        gallery = extract_gallery(page_html, pages[lang], product_slug, existing_map)
        if lang == "zh" and cjk_count(product.get("title", {}).get("zh", "")) > 0:
            # Parete often serves Chinese gallery images with English alt/title
            # text. Keep our normalized product title for the Chinese gallery.
            for item in gallery:
                item["alt"] = product["title"]["zh"]
                item["caption"] = product["title"]["zh"]
        for item in gallery:
            if download_image(item["original_url"], item["path"], scrape_root):
                stats["downloaded"] += 1
        product.setdefault("gallery", {})[lang] = gallery
        stats["gallery"][lang] = len(gallery)

        live_desc = extract_description_html(page_html)
        rewritten_desc, body_count, body_downloaded = rewrite_description_images(live_desc, pages[lang], product_slug, existing_map, scrape_root)
        stats["body_images"][lang] = body_count
        stats["downloaded"] += body_downloaded

        live_text = strip_tags(live_desc)
        current_text = product.get("description", {}).get(lang, {}).get("text", "")
        should_preserve = lang == "zh" and cjk_count(live_text) < 50
        if should_preserve:
            current_html = product["description"][lang]["html"]
            rewritten_current, current_body_count, current_downloaded = rewrite_description_images(current_html, pages[lang], product_slug, existing_map, scrape_root)
            product["description"][lang]["html"] = rewritten_current
            stats["body_images"][lang] = current_body_count
            stats["downloaded"] += current_downloaded
            stats["preserved_zh_description"] = True
        else:
            product.setdefault("description", {}).setdefault(lang, {})
            product["description"][lang]["html"] = rewritten_desc
            product["description"][lang]["text"] = live_text

        if lang == "en":
            fetched_summary = extract_summary(page_html)
            existing_summary = product.get("summary", {}).get(lang, {})
            product.setdefault("summary", {})[lang] = {
                key: (value if value else existing_summary.get(key, ""))
                for key, value in fetched_summary.items()
            }
            product.setdefault("summary_text", {})[lang] = strip_tags(extract_summary_html(page_html))
            product.setdefault("specifications", {})[lang] = extract_specs(page_html)
            product.setdefault("downloads", {})[lang] = extract_downloads(page_html, pages[lang])
        elif not stats["preserved_zh_description"]:
            product.setdefault("specifications", {})[lang] = extract_specs(page_html)
            product.setdefault("downloads", {})[lang] = extract_downloads(page_html, pages[lang])

    if not args.dry_run:
        products_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "product_id": product.get("id"),
        "slug": product_slug,
        "stats": stats,
        "updated": not args.dry_run,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
