#!/usr/bin/env python3
"""
Sunfly products-catalog build script.

Input:
  parete-scrape/products.json  (scraped & bilingual-normalized, 24 products)
  parete-scrape/images/        (local image bundle)

Output (into the live site tree):
  products/index.html                                   (hub stub)
  products/anti-static-access-floor/index.html          (category grid)
  products/anti-static-access-floor/<slug>/index.html   (per-SKU pages)
  assets/products/<slug>/                               (mirrored images)
  assets/datasheets/                                    (empty for now — parete PDFs are 0-byte upstream)

Transformations enforced:
  - "Parete" / "PARETE" stripped from rendered content (kept in internal JSON).
  - "PRT-" SKU prefix rewritten to "SF-".
  - Simplified Chinese (zh-CN) run through OpenCC s2hk for the primary 繁 content.
  - Pricing / MOQ / packing / production / delivery / payment / supply info
    NEVER rendered on public HTML — all commercial routes through quote form.

Usage:
  python3 tools/build_products.py [--only-slug 2-steel-access-floor-hpl]
                                  [--skip-images] [--site-root <path>]

The script is idempotent — it overwrites output files cleanly on each run.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from opencc import OpenCC
except ImportError:
    sys.exit("opencc-python-reimplemented required: pip install opencc --break-system-packages")

REPO_ROOT_DEFAULT = Path("/sessions/nice-admiring-euler/mnt/website-project")

CATEGORY_SLUG = "anti-static-access-floor"
CATEGORY_I18N = {
    "EN": "Anti-Static Access Floor Systems",
    "繁": "防靜電架空地板系統",
    "简": "防静电架空地板系统",
}

# s2hkm uses zh-HK-specific phrases where available; fall back to s2hk otherwise.
_s2hk = OpenCC("s2hkm" if (Path(OpenCC.__module__.rsplit(".", 1)[0]).exists()) else "s2hk")
# (Just construct both and pick; OpenCC constructor is cheap.)
_s2hk = OpenCC("s2hk")


def to_zh_hk(text: str) -> str:
    """Convert simplified-Chinese text to zh-HK traditional."""
    if not text:
        return text
    return _s2hk.convert(text)


# ----- Rewriting -------------------------------------------------------------

_PARETE_RE = re.compile(r"\bparete\b", re.IGNORECASE)
_SKU_PRT_RE = re.compile(r"\bPRT-")


def strip_brand(text: str) -> str:
    """Remove Parete references from user-facing strings."""
    if not text:
        return text
    # Replace brand word first
    text = _PARETE_RE.sub("Sunfly", text)
    # Rewrite SKU prefixes
    text = _SKU_PRT_RE.sub("SF-", text)
    return text


def sunfly_sku_codes(raw: str) -> list[str]:
    """Given 'PRT-FS662, PRT-FS800, PRT-FS1000' -> ['SF-FS662','SF-FS800','SF-FS1000']."""
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    return [strip_brand(p) for p in parts]


def tidy_title(text: str) -> str:
    """Clean a product title for display. Strips the leading 'AF-1-' / 'VF-7-' kind
    of series prefix that Parete uses as an internal ordering and returns a cleaner
    human title while still preserving the series code as a separate badge."""
    return text  # keep as-is for v1; the AF-/VF-/C- codes ARE the series identifier we want


_SERIES_RE = re.compile(
    r"^(?P<code>"
    r"[A-Z]{1,3}"                               # letters: AF, VF, C, PRT ...
    r"[\s\u00A0\u2013\u2014-]?"                 # optional separator
    r"\d+[A-Z]?"                                # digit(s), optional trailing letter (e.g. C4)
    r"(?:[\s\u00A0\u2013\u2014-]+(?:[A-Z0-9]{2,}))?"    # optional 2nd group: -OA, -0A, -600
    r"(?:[\s\u00A0\u2013\u2014-]+\d+)?"         # optional 3rd group (e.g. 600)
    r")"
    r"(?=[\s\u00A0\u2013\u2014-]|$)"            # must end at separator or end of string
)


def series_code(title: str) -> str:
    """Extract the short series code from a product title, e.g.
    'AF-1-Steel access floor...' -> 'AF-1',
    'VF-1-Steel Ventilation...' -> 'VF-1',
    'C4-OA 600 Bracing Support...' -> 'C4-OA-600'."""
    t = title.strip()
    m = _SERIES_RE.match(t)
    if not m:
        return ""
    code = m.group("code")
    # normalize: collapse whitespace / en-dashes / em-dashes / dashes into single '-'
    code = re.sub(r"[\s\u00A0\u2013\u2014-]+", "-", code).strip("-")
    return code


def display_title(title: str) -> str:
    """Strip the series prefix from a title for the main heading."""
    t = title.strip()
    m = _SERIES_RE.match(t)
    if m:
        rest = t[m.end():].lstrip(" -\u2013\u2014")
        return rest or title
    return title


_STOPWORDS = {
    "the", "a", "an", "with", "and", "of", "for", "system", "systems",
    "raised", "access", "anti", "static", "floor", "series",
}


def _disambiguator(product: dict) -> str:
    """Pick a single short descriptor word from the title to disambiguate
    products that share a series code (e.g. C4-OA-600 variants)."""
    rest = display_title(product["title"]["en"]).lower()
    rest = re.sub(r"[^a-z0-9\s-]", " ", rest)
    words = [w for w in re.split(r"[\s-]+", rest) if w]
    for w in words:
        if w in _STOPWORDS or w.isdigit():
            continue
        return w
    return str(product["id"])


def assign_public_slugs(products: list[dict]) -> dict[Any, str]:
    """Return {product_id: unique_public_slug}.

    Primary slug = lowercase series code (e.g. 'af-1', 'vf-5', 'c4-oa-600').
    When two products share a series code, both get disambiguated by title
    (e.g. 'c4-oa-600-stringer' vs 'c4-oa-600-bracing')."""
    bases: dict[Any, str] = {}
    seen: dict[str, list[Any]] = {}
    for p in products:
        sc = series_code(p["title"]["en"]).lower()
        base = sc if sc else re.sub(r"^\d+-", "", p["slug"])
        bases[p["id"]] = base
        seen.setdefault(base, []).append(p["id"])

    # Disambiguate collisions — append a 1-word title descriptor to ALL
    # collision members (not just second+) so URLs are predictable.
    final: dict[Any, str] = {}
    by_id = {p["id"]: p for p in products}
    for base, ids in seen.items():
        if len(ids) == 1:
            final[ids[0]] = base
        else:
            for pid in ids:
                disambig = _disambiguator(by_id[pid])
                final[pid] = f"{base}-{disambig}"
    return final


# ----- Description parsing --------------------------------------------------

def split_description(text: str) -> dict:
    """Parse the long-form description into sections.

    Recognizes headings:
      - 'Product discription' / 'Product description' / '产品描述' / '產品描述'
      - 'Product advantages:' / '产品优势' / '產品優勢'
      - 'Technical data ...' / '技术参数' / '技術參數'
      - 'HPL covering' / 'PVC covering' etc. -- merged into 'covering' section
      - 'Applications' / '应用领域' / '應用領域'
    """
    if not text:
        return {}
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    sections: dict[str, list[str]] = {
        "title": [],
        "description": [],
        "advantages": [],
        "covering": [],
        "applications": [],
    }
    current = "title"
    # If first line looks like a title, consume it
    first_used = False

    head_map = [
        (re.compile(r"^product\s+discription\b|^product\s+description\b", re.I), "description"),
        (re.compile(r"^产品描述|^產品描述"), "description"),
        (re.compile(r"^product\s+advantages?\b", re.I), "advantages"),
        (re.compile(r"^产品优势|^產品優勢"), "advantages"),
        (re.compile(r"^technical\s+data\b", re.I), "covering"),
        # Chinese "technical data" line often has a product-type prefix,
        # e.g. "钢制防静电活动地板技术参数" → still a heading. Allow up to ~25
        # chars of prefix before the keyword, anchored at end-of-line.
        (re.compile(r"^.{0,25}(?:技术参数|技術參數|技術資料)\s*$"), "covering"),
        (re.compile(r"^applications?\b", re.I), "applications"),
        (re.compile(r"^应用领域|^應用領域|^應用范圍|^应用范围"), "applications"),
    ]
    for line in lines:
        matched = False
        for rx, target in head_map:
            if rx.match(line):
                current = target
                matched = True
                break
        if matched:
            continue
        if not first_used and current == "title":
            sections["title"].append(line)
            first_used = True
            current = "description"
            continue
        sections[current].append(line)
    # compact lists of bullet lines: strip leading digits and dots
    def norm_bullets(lst: list[str]) -> list[str]:
        out = []
        for l in lst:
            l = re.sub(r"^\s*(\d+\.|[-•])\s*", "", l).strip()
            if l:
                out.append(l)
        return out

    return {
        "heading": " ".join(sections["title"]).strip(),
        "description": sections["description"],
        "advantages": norm_bullets(sections["advantages"]),
        "covering": sections["covering"],
        "applications": norm_bullets(sections["applications"]),
    }


# ----- Description HTML parser (images + captions per section) -------------

_P_BLOCK_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.I | re.DOTALL)
_IMG_RE = re.compile(r"<img\s+([^>]*)>", re.I)
_ATTR_RE = re.compile(r'([a-zA-Z_:-][a-zA-Z0-9_:-]*)\s*=\s*"([^"]*)"')


def _attrs_from(tag: str) -> dict:
    return {m.group(1).lower(): m.group(2) for m in _ATTR_RE.finditer(tag)}


def _strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?\s*>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


def parse_description_media(html_text: str) -> dict:
    """Walk description HTML <p> blocks in order, detect section boundaries
    (same patterns as split_description) and bucket images and caption-text
    that appears immediately under an image into each section.

    Returns:
      {
        "description": {"images": [{src, alt}, ...]},
        "covering":    {"images": [...]},
        "applications":{"pairs":  [{src, alt, caption}, ...]},
      }
    Applications are returned as (image, caption) pairs because on Parete each
    applications image is followed by a short underlined caption in its own <p>.
    """
    if not html_text:
        return {"description": {"images": []}, "covering": {"images": []}, "applications": {"pairs": []}}

    # Same section heading matcher as split_description — keep in sync.
    head_map = [
        (re.compile(r"^product\s+discription\b|^product\s+description\b", re.I), "description"),
        (re.compile(r"^产品描述|^產品描述"), "description"),
        (re.compile(r"^product\s+advantages?\b", re.I), "advantages"),
        (re.compile(r"^产品优势|^產品優勢"), "advantages"),
        (re.compile(r"^technical\s+data\b", re.I), "covering"),
        (re.compile(r"^.{0,25}(?:技术参数|技術參數|技術資料)\s*$"), "covering"),
        (re.compile(r"^applications?\b", re.I), "applications"),
        (re.compile(r"^应用领域|^應用領域|^應用范圍|^应用范围"), "applications"),
    ]

    buckets = {
        "description": {"images": []},
        "advantages": {"images": []},
        "covering": {"images": []},
        "applications": {"pairs": []},
    }
    current = "description"
    pending_img = None  # for applications: image waiting for its caption

    for m in _P_BLOCK_RE.finditer(html_text):
        inner = m.group(1)
        # Is this an image paragraph?
        img_m = _IMG_RE.search(inner)
        if img_m:
            attrs = _attrs_from(img_m.group(0))
            src = attrs.get("src", "")
            alt = attrs.get("alt", "") or attrs.get("title", "")
            if current == "applications":
                # Start a new pair (previous pending_img is abandoned; shouldn't happen)
                pending_img = {"src": src, "alt": alt, "caption": ""}
                buckets["applications"]["pairs"].append(pending_img)
            else:
                buckets[current]["images"].append({"src": src, "alt": alt})
            continue

        text = _strip_tags(inner)
        if not text:
            continue

        # Section heading?
        matched_heading = False
        for rx, target in head_map:
            if rx.match(text):
                current = target
                matched_heading = True
                pending_img = None
                break
        if matched_heading:
            continue

        # In applications: a plain-text line right after an image is its caption
        if current == "applications" and pending_img is not None and not pending_img["caption"]:
            pending_img["caption"] = text
            pending_img = None

    return buckets


def stage_description_images(product: dict, scrape_root, dest_root, public_slug: str, skip_images: bool = False) -> dict:
    """Copy every image referenced inside the product's description HTML into
    assets/products/<public_slug>/desc/<fname>. Returns a src-rewrite map:
      {original_relative_src: web_absolute_path}
    """
    import shutil as _sh
    from pathlib import Path as _P

    html_en = product.get("description", {}).get("en", {}).get("html") or ""
    html_zh = product.get("description", {}).get("zh", {}).get("html") or ""
    all_imgs = set()
    for h in (html_en, html_zh):
        for m in _IMG_RE.finditer(h):
            attrs = _attrs_from(m.group(0))
            if attrs.get("src"):
                all_imgs.add(attrs["src"])

    src_root = _P(scrape_root)
    dest_dir = _P(dest_root) / "assets" / "products" / public_slug / "desc"
    dest_dir.mkdir(parents=True, exist_ok=True)

    rewrite = {}
    for rel_src in all_imgs:
        # Scrape uses relative paths like "images/2-steel-access-floor-hpl/foo.png"
        # or "images/shared/foo.jpg". Resolve against parete-scrape/.
        if rel_src.startswith(("http://", "https://")):
            continue  # upstream URL we cannot mirror safely; skip
        src_file = src_root / rel_src
        if not src_file.is_file():
            # Some images may not have been downloaded; skip silently
            continue
        fname = src_file.name
        target = dest_dir / fname
        if not skip_images:
            if not target.exists() or target.stat().st_size != src_file.stat().st_size:
                _sh.copy2(src_file, target)
        rewrite[rel_src] = f"/assets/products/{public_slug}/desc/{fname}"
    return rewrite


# ----- HTML helpers ---------------------------------------------------------

def esc(s: str | None) -> str:
    return html.escape(s or "", quote=True)


def render_header(active: str = "") -> str:
    """Shared site header — matches index.html style."""
    return r"""
<!-- Header (shared) -->
<header id="header" class="sticky top-0 z-50 bg-white shadow-sm">
  <div class="bg-slate-800 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
      <div class="flex justify-between items-center gap-4">
        <div class="flex items-center gap-6">
          <a href="tel:+85256441916" class="flex items-center gap-2 hover:text-orange-400 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
            <span class="text-sm hidden sm:block">+852 5644 1916</span>
          </a>
          <a href="mailto:enquiery@sunfly.hk" class="flex items-center gap-2 hover:text-orange-400 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            <span class="text-sm hidden sm:block">enquiery@sunfly.hk</span>
          </a>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="changeLanguage('EN')" id="lang-en" class="text-sm px-2 py-1 rounded transition-colors bg-orange-500 text-white">EN</button>
          <span class="text-slate-400">|</span>
          <button onclick="changeLanguage('繁')" id="lang-tc" class="text-sm px-2 py-1 rounded transition-colors hover:text-orange-400">繁</button>
          <span class="text-slate-400">|</span>
          <button onclick="changeLanguage('简')" id="lang-sc" class="text-sm px-2 py-1 rounded transition-colors hover:text-orange-400">简</button>
        </div>
      </div>
    </div>
  </div>
  <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-20">
      <a href="/" class="flex items-center gap-2">
        <div class="w-10 h-10 bg-orange-500 rounded flex items-center justify-center"><span class="text-white text-xs">SF</span></div>
        <span class="text-slate-900">Sunfly</span>
      </a>
      <div class="hidden md:flex items-center gap-8">
        <a href="/" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.home"></a>
        <a href="/products/anti-static-access-floor/" class="text-orange-500 font-semibold transition-colors" data-i18n="nav.products"></a>
        <a href="/#job-reference" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.jobReference"></a>
        <a href="/#about" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.about"></a>
        <a href="/#services" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.services"></a>
        <a href="/#culture" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.culture"></a>
        <a href="/#contact" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.contact"></a>
        <button onclick="openQuoteModal()" class="bg-orange-500 text-white px-6 py-2 rounded hover:bg-orange-600 transition-colors" data-i18n="nav.getQuote"></button>
      </div>
      <button class="md:hidden" onclick="toggleMobileMenu()">
        <svg id="menu-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        <svg id="close-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>
    <div id="mobile-menu" class="hidden md:hidden py-4 border-t">
      <div class="flex flex-col gap-4">
        <a href="/" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.home"></a>
        <a href="/products/anti-static-access-floor/" class="text-orange-500 font-semibold" data-i18n="nav.products"></a>
        <a href="/#job-reference" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.jobReference"></a>
        <a href="/#about" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.about"></a>
        <a href="/#services" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.services"></a>
        <a href="/#culture" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.culture"></a>
        <a href="/#contact" class="text-slate-600 hover:text-orange-500 transition-colors" data-i18n="nav.contact"></a>
      </div>
    </div>
  </nav>
</header>
""".strip()


def render_footer() -> str:
    return r"""
<footer class="bg-slate-900 text-white mt-20">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
      <div>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-10 h-10 bg-orange-500 rounded flex items-center justify-center"><span class="text-xs">SF</span></div>
          <span>Sunfly</span>
        </div>
        <p class="text-slate-400 mb-4" data-i18n="footer.about.desc"></p>
      </div>
      <div>
        <h3 class="text-white mb-4" data-i18n="nav.home"></h3>
        <ul class="space-y-2">
          <li><a href="/" class="text-slate-400 hover:text-orange-400 transition-colors" data-i18n="nav.home"></a></li>
          <li><a href="/products/anti-static-access-floor/" class="text-slate-400 hover:text-orange-400 transition-colors" data-i18n="nav.products"></a></li>
          <li><a href="/#about" class="text-slate-400 hover:text-orange-400 transition-colors" data-i18n="nav.about"></a></li>
          <li><a href="/#contact" class="text-slate-400 hover:text-orange-400 transition-colors" data-i18n="nav.contact"></a></li>
        </ul>
      </div>
      <div>
        <h3 class="text-white mb-4" data-i18n="footer.products.title"></h3>
        <ul class="space-y-2">
          <li><a href="/products/anti-static-access-floor/" class="text-slate-400 hover:text-orange-400 transition-colors" data-i18n="products.raisedFloor.name"></a></li>
          <li class="text-slate-400" data-i18n="products.ceiling.name"></li>
          <li class="text-slate-400" data-i18n="products.glazing.name"></li>
          <li class="text-slate-400" data-i18n="products.steelFraming.name"></li>
        </ul>
      </div>
      <div>
        <h3 class="text-white mb-4" data-i18n="footer.contact.title"></h3>
        <ul class="space-y-2 text-slate-400">
          <li data-i18n="contact.info.addressValue"></li>
          <li><a href="tel:+85256441916" class="hover:text-orange-400 transition-colors">+852 5644 1916</a></li>
          <li><a href="mailto:enquiery@sunfly.hk" class="hover:text-orange-400 transition-colors">enquiery@sunfly.hk</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-slate-800 pt-8 text-center text-slate-400 text-sm">
      <p data-i18n="footer.copyright"></p>
    </div>
  </div>
</footer>
""".strip()


def render_quote_modal() -> str:
    """Floating quote-cart button + modal. Single SKU for v1, with a note that
    the cart can hold multiple SKUs once the rest of the catalog is generated."""
    return r"""
<!-- Floating quote-cart button -->
<button id="quote-cart-btn" onclick="openQuoteModal()"
        class="fixed bottom-6 right-6 z-50 bg-orange-500 hover:bg-orange-600 text-white rounded-full shadow-2xl px-5 py-4 flex items-center gap-2 transition-all">
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
  <span data-i18n="quote.cartButton"></span>
  <span id="quote-cart-count" class="bg-white text-orange-600 rounded-full w-6 h-6 text-sm font-bold flex items-center justify-center">0</span>
</button>

<!-- Quote modal -->
<div id="quote-modal" class="hidden fixed inset-0 z-[60] bg-slate-900/70 items-center justify-center p-4">
  <div class="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
    <div class="flex justify-between items-center p-6 border-b">
      <h3 class="text-slate-900 text-xl font-semibold" data-i18n="quote.modalTitle"></h3>
      <button onclick="closeQuoteModal()" class="text-slate-500 hover:text-slate-900 text-2xl leading-none">&times;</button>
    </div>
    <div class="p-6">
      <div id="quote-cart-items" class="mb-6"></div>
      <form id="quote-form" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="contact.form.name"></span> *</label>
            <input type="text" name="name" required class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500">
          </div>
          <div>
            <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="contact.form.email"></span> *</label>
            <input type="email" name="email" required class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500">
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="contact.form.phone"></span></label>
            <input type="tel" name="phone" class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500">
          </div>
          <div>
            <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="quote.company"></span></label>
            <input type="text" name="company" class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500">
          </div>
        </div>
        <div>
          <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="quote.quantity"></span></label>
          <input type="text" name="quantity" placeholder="e.g. 500 m²" class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500">
        </div>
        <div>
          <label class="block text-slate-700 mb-1 text-sm"><span data-i18n="contact.form.message"></span> *</label>
          <textarea name="message" rows="4" required class="w-full px-3 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"></textarea>
        </div>
        <!-- Hidden packed cart field — will be filled by JS before submit -->
        <input type="hidden" name="items" id="quote-items-hidden">
        <button type="submit" class="w-full bg-orange-500 text-white px-6 py-3 rounded hover:bg-orange-600 transition-colors" data-i18n="quote.submit"></button>
      </form>
    </div>
  </div>
</div>
""".strip()


def render_quote_js() -> str:
    """In-memory quote cart (sessionStorage fallback). Uses EmailJS when available."""
    return r"""
<script>
  (function () {
    // Minimal quote cart. In-memory only; resets on navigation.
    // TODO(post-approval): promote to sessionStorage so it survives page jumps
    //                      inside /products/.
    window.__quoteCart = window.__quoteCart || [];

    window.addToQuote = function (sku, title) {
      if (!sku) return;
      if (window.__quoteCart.find(function (x) { return x.sku === sku; })) {
        openQuoteModal();
        return;
      }
      window.__quoteCart.push({ sku: sku, title: title });
      renderCart();
      flashCartButton();
    };

    window.removeFromQuote = function (sku) {
      window.__quoteCart = window.__quoteCart.filter(function (x) { return x.sku !== sku; });
      renderCart();
    };

    function flashCartButton() {
      var btn = document.getElementById('quote-cart-btn');
      if (!btn) return;
      btn.classList.add('scale-110');
      setTimeout(function () { btn.classList.remove('scale-110'); }, 200);
    }

    function renderCart() {
      var count = document.getElementById('quote-cart-count');
      if (count) count.textContent = String(window.__quoteCart.length);
      var host = document.getElementById('quote-cart-items');
      if (!host) return;
      if (!window.__quoteCart.length) {
        host.innerHTML = '<p class="text-slate-500 text-sm">' + (t('quote.empty') || 'No products selected yet. Browse the catalog and click "Add to quote" on any product.') + '</p>';
      } else {
        host.innerHTML = '<div class="mb-4"><p class="text-sm text-slate-600 mb-2">' + (t('quote.itemsLabel') || 'Products in your quote:') + '</p><ul class="divide-y border rounded">' +
          window.__quoteCart.map(function (it) {
            return '<li class="flex justify-between items-center px-3 py-2 text-sm">' +
                   '<span><span class="font-mono text-slate-500">' + it.sku + '</span> &middot; ' + it.title + '</span>' +
                   '<button type="button" onclick="removeFromQuote(\'' + it.sku + '\')" class="text-slate-400 hover:text-red-500" aria-label="remove">&times;</button>' +
                   '</li>';
          }).join('') + '</ul></div>';
      }
    }

    window.openQuoteModal = function () {
      var m = document.getElementById('quote-modal');
      if (!m) return;
      m.classList.remove('hidden');
      m.classList.add('flex');
      renderCart();
    };
    window.closeQuoteModal = function () {
      var m = document.getElementById('quote-modal');
      if (!m) return;
      m.classList.add('hidden');
      m.classList.remove('flex');
    };

    document.addEventListener('DOMContentLoaded', function () {
      renderCart();
      var form = document.getElementById('quote-form');
      if (form) {
        form.addEventListener('submit', function (ev) {
          ev.preventDefault();
          // Pack cart into items hidden field
          var items = window.__quoteCart.map(function (it) { return it.sku + ' — ' + it.title; }).join('\n');
          document.getElementById('quote-items-hidden').value = items || '(no SKUs pinned — general enquiry)';

          var submitBtn = form.querySelector('button[type="submit"]');
          var originalText = submitBtn.textContent;
          submitBtn.disabled = true;
          submitBtn.textContent = t('quote.sending') || 'Sending…';

          if (typeof emailjs === 'undefined') {
            alert('EmailJS not loaded — please try again from the main contact form.');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
            return;
          }
          emailjs.sendForm('default_service', 'template_czus2pw', form)
            .then(function () {
              alert(t('quote.success') || 'Thanks — your quote request was received. We will reply within one business day.');
              form.reset();
              window.__quoteCart = [];
              renderCart();
              closeQuoteModal();
            })
            .catch(function (err) {
              console.error('quote send error', err);
              alert('Sorry, there was an error sending your request. Please email enquiery@sunfly.hk directly.');
            })
            .finally(function () {
              submitBtn.disabled = false;
              submitBtn.textContent = originalText;
            });
        });
      }
    });
  })();
</script>
""".strip()


# ----- Common <head> --------------------------------------------------------

def render_head(page_title: str, meta_desc: str, canonical: str, alt_langs: dict[str, str] | None = None) -> str:
    # alt_langs: lang_code -> href
    alt_link_tags = "\n    ".join(
        f'<link rel="alternate" hreflang="{esc(lang)}" href="{esc(href)}">' for lang, href in (alt_langs or {}).items()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(page_title)}</title>
    <meta name="description" content="{esc(meta_desc)}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{esc(canonical)}">
    {alt_link_tags}
    <meta property="og:type" content="website">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:site_name" content="Sunfly Building Materials">
    <meta property="og:title" content="{esc(page_title)}">
    <meta property="og:description" content="{esc(meta_desc)}">
    <meta property="og:locale" content="en_HK">
    <meta property="og:locale:alternate" content="zh_HK">
    <meta property="og:locale:alternate" content="zh_CN">
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <script src="/assets/tailwindcss-3_4_17.css"></script>
    <script>
      tailwind.config = {{
        theme: {{ extend: {{ colors: {{
          slate: {{ 50:'#f8fafc', 300:'#cbd5e1', 400:'#94a3b8', 600:'#475569', 700:'#334155', 800:'#1e293b', 900:'#0f172a' }},
          orange: {{ 100:'#ffedd5', 400:'#fb923c', 500:'#f97316', 600:'#ea580c' }},
          blue: {{ 100:'#dbeafe', 500:'#3b82f6', 600:'#2563eb' }},
        }} }} }}
      }}
    </script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ min-width:300px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Helvetica Neue',Arial,sans-serif; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale; }}
      h1 {{ font-size:2.25rem; font-weight:700; line-height:2.5rem; }}
      h2 {{ font-size:1.875rem; font-weight:700; }}
      h3 {{ font-size:1.25rem; font-weight:600; }}
      h4 {{ font-size:1.05rem; font-weight:600; }}
      .smooth-scroll {{ scroll-behavior:smooth; }}
      /* Gallery hover */
      .gallery-thumb.active {{ ring: 2px solid #f97316; border-color: #f97316; }}
    </style>
</head>
<body class="min-h-screen bg-white">
"""


def render_body_end(product_translations_js: str, list_expander_js: str = "") -> str:
    """Scripts that close the page. The product_translations_js extends the
    global `translations` object before main.js's DOMContentLoaded handler
    runs. The list_expander must run AFTER main.js so its wrapper of
    window.changeLanguage is not clobbered by main.js's own declaration."""
    return f"""
<!-- EmailJS -->
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
<!-- Global translations (shared with homepage) -->
<script src="/js/translations.js"></script>
<!-- Per-page additions -->
<script>
{product_translations_js}
</script>
<!-- Shared site behavior -->
<script src="/js/main.js"></script>
{list_expander_js}
{render_quote_js()}
</body>
</html>
"""


# ----- Gallery + image staging ---------------------------------------------

def stage_product_assets(product: dict, scrape_root: Path, dest_root: Path, public_slug: str, skip_images: bool = False) -> dict:
    """Copy a product's images from parete-scrape/images/<scrape_slug>/ into
    assets/products/<public_slug>/ and return the rewritten gallery entries.
    public_slug is assigned by assign_public_slugs() for uniqueness across SKUs."""
    scrape_slug = product["slug"]
    src_dir = scrape_root / "images" / scrape_slug
    dest_dir = dest_root / "assets" / "products" / public_slug
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not skip_images and src_dir.is_dir():
        for img in src_dir.iterdir():
            if img.is_file():
                target = dest_dir / img.name
                if not target.exists() or target.stat().st_size != img.stat().st_size:
                    shutil.copy2(img, target)
    # Rewrite gallery paths — use EN gallery as canonical (paths are shared between EN/ZH typically)
    new_gallery = []
    for entry in product["gallery"]["en"]:
        fname = Path(entry["path"]).name
        # prefer EN-captioned variant; zh-CN variants have "-cn" suffix on parete,
        # drop zh-CN-only shots from the public gallery to keep it tight.
        if "-cn." in fname.lower():
            continue
        new_gallery.append({
            "src": f"/assets/products/{public_slug}/{fname}",
            "alt_en": entry.get("alt") or entry.get("caption") or "",
        })
    # Also pick a thumbnail
    thumb = product.get("thumbnail") or {}
    if thumb.get("path"):
        fname = Path(thumb["path"]).name
        thumb_src = f"/assets/products/{public_slug}/{fname}"
    else:
        thumb_src = new_gallery[0]["src"] if new_gallery else ""
    return {"public_slug": public_slug, "gallery": new_gallery, "thumb": thumb_src}


# ----- Per-product translation shape ---------------------------------------

def product_i18n_payload(product: dict) -> dict:
    """Build EN / 繁 / 简 string sets for a single product. Uses the ZH scraped
    text as zh-CN, OpenCC-converts to zh-HK for 繁."""
    title_en = strip_brand(display_title(product["title"]["en"]))
    title_sc = strip_brand(display_title(product["title"]["zh"]))
    title_tc = to_zh_hk(title_sc)

    series = series_code(product["title"]["en"])

    desc_en = split_description(strip_brand(product["description"]["en"]["text"]))
    desc_sc = split_description(strip_brand(product["description"]["zh"]["text"]))
    desc_tc = split_description(to_zh_hk(strip_brand(product["description"]["zh"]["text"])))

    cat_en = product["category"]["en"]
    cat_sc = product["category"]["zh"]
    cat_tc = to_zh_hk(cat_sc)

    return {
        "EN": {
            "title": title_en,
            "series": series,
            "category": cat_en,
            "desc_heading": desc_en["heading"],
            "desc_description": desc_en["description"],
            "desc_advantages": desc_en["advantages"],
            "desc_covering": desc_en["covering"],
            "desc_applications": desc_en["applications"],
        },
        "繁": {
            "title": title_tc,
            "series": series,
            "category": cat_tc,
            "desc_heading": desc_tc["heading"],
            "desc_description": desc_tc["description"],
            "desc_advantages": desc_tc["advantages"],
            "desc_covering": desc_tc["covering"],
            "desc_applications": desc_tc["applications"],
        },
        "简": {
            "title": title_sc,
            "series": series,
            "category": cat_sc,
            "desc_heading": desc_sc["heading"],
            "desc_description": desc_sc["description"],
            "desc_advantages": desc_sc["advantages"],
            "desc_covering": desc_sc["covering"],
            "desc_applications": desc_sc["applications"],
        },
    }


# ----- Per-SKU page ---------------------------------------------------------

# Static labels used across the product page template.
# Mapped to the existing translations.js language keys (EN / 繁 / 简).
COMMON_LABELS = {
    "product.series": {"EN": "Series", "繁": "系列", "简": "系列"},
    "product.sku": {"EN": "SKU", "繁": "型號", "简": "型号"},
    "product.overview": {"EN": "Overview", "繁": "產品概覽", "简": "产品概览"},
    "product.advantages": {"EN": "Key Advantages", "繁": "主要優勢", "简": "主要优势"},
    "product.covering": {"EN": "Technical Notes", "繁": "技術說明", "简": "技术说明"},
    "product.applications": {"EN": "Applications", "繁": "應用場景", "简": "应用场景"},
    "product.datasheet": {"EN": "Full Datasheet", "繁": "完整產品資料", "简": "完整产品资料"},
    "product.datasheetCta": {
        "EN": "Request the full technical datasheet as part of your quote",
        "繁": "索取完整技術資料，將隨報價一併提供",
        "简": "索取完整技术资料，将随报价一并提供",
    },
    "product.requestQuote": {"EN": "Request a Quote", "繁": "索取報價", "简": "索取报价"},
    "product.addToQuote": {"EN": "Add to Quote", "繁": "加入報價單", "简": "加入报价单"},
    "product.inCart": {"EN": "Added to quote", "繁": "已加入報價單", "简": "已加入报价单"},
    "product.backToCategory": {"EN": "Back to all products", "繁": "返回所有產品", "简": "返回所有产品"},
    "quote.cartButton": {"EN": "Quote Request", "繁": "報價請求", "简": "报价请求"},
    "quote.modalTitle": {"EN": "Request a Quote", "繁": "索取報價", "简": "索取报价"},
    "quote.empty": {
        "EN": 'No products selected yet. Browse the catalog and click "Add to quote" on any product.',
        "繁": "尚未加入任何產品。請在目錄中選取您感興趣的產品。",
        "简": "尚未加入任何产品。请在目录中选取您感兴趣的产品。",
    },
    "quote.itemsLabel": {"EN": "Products in your quote:", "繁": "已加入的產品：", "简": "已加入的产品："},
    "quote.company": {"EN": "Company", "繁": "公司", "简": "公司"},
    "quote.quantity": {"EN": "Estimated quantity", "繁": "預計數量", "简": "预计数量"},
    "quote.submit": {"EN": "Send Request", "繁": "送出請求", "简": "发送请求"},
    "quote.sending": {"EN": "Sending…", "繁": "傳送中…", "简": "发送中…"},
    "quote.success": {
        "EN": "Thanks — your quote request was received. We'll reply within one business day.",
        "繁": "感謝您的查詢，我們將於一個工作天內回覆。",
        "简": "感谢您的查询，我们将于一个工作日内回复。",
    },
    "category.title": CATEGORY_I18N,
    "category.subtitle": {
        "EN": "Browse our full range of anti-static and ventilation access floor systems for computer rooms, data centers and control rooms.",
        "繁": "瀏覽我們為機房、數據中心與控制室提供的防靜電及通風架空地板系統系列。",
        "简": "浏览我们为机房、数据中心与控制室提供的防静电及通风架空地板系统系列。",
    },
    "category.viewDetails": {"EN": "View details", "繁": "查看詳情", "简": "查看详情"},
}


def build_translations_js_block(extra: dict[str, dict[str, str | list[str]]]) -> str:
    """Return a JS snippet that merges `extra` into the global translations
    object, where extra is shaped as {key: {EN: ..., 繁: ..., 简: ...}}.

    For list values, joins with double-newline so the t() helper returns a
    single string we can split client-side if needed. Lists are short enough
    that we instead emit dedicated enumerated keys (foo.0, foo.1, ...) so
    main.js' t() stays unchanged.
    """
    flat: dict[str, dict[str, str]] = {}
    for k, by_lang in extra.items():
        # If any language value is a list, fan out to indexed keys and also
        # emit a `.count` key. Otherwise keep as-is.
        sample = next(iter(by_lang.values()))
        if isinstance(sample, list):
            max_n = max(len(v) for v in by_lang.values())
            for i in range(max_n):
                flat[f"{k}.{i}"] = {lang: (by_lang[lang][i] if i < len(by_lang[lang]) else "") for lang in by_lang}
            flat[f"{k}.count"] = {lang: str(max_n) for lang in by_lang}
        else:
            flat[k] = {lang: str(v) for lang, v in by_lang.items()}

    # Emit as JS that mutates `translations`.
    lines = ["(function(){"]
    lines.append("  if (typeof translations === 'undefined') return;")
    for lang in ["EN", "繁", "简"]:
        per = {k: v[lang] for k, v in flat.items() if lang in v}
        if not per:
            continue
        lines.append(f"  Object.assign(translations[{json.dumps(lang)}], {json.dumps(per, ensure_ascii=False)});")
    lines.append("})();")
    return "\n".join(lines)


def render_sku_page(product: dict, scrape_root: Path, dest_root: Path, public_slug: str, skip_images: bool = False) -> Path:
    staged = stage_product_assets(product, scrape_root, dest_root, public_slug, skip_images=skip_images)
    gallery = staged["gallery"]

    # Description body images (intro photos, technical data charts, application
    # photos) live inline in the parete description HTML. Stage them locally and
    # build a section-indexed media dict we can inject into each section below.
    desc_src_rewrite = stage_description_images(product, scrape_root, dest_root, public_slug, skip_images=skip_images)
    desc_media_en = parse_description_media(product.get("description", {}).get("en", {}).get("html") or "")

    def _rewrite_img(src: str) -> str:
        return desc_src_rewrite.get(src, src)

    i18n = product_i18n_payload(product)
    series = i18n["EN"]["series"]
    skus = sunfly_sku_codes(product.get("summary", {}).get("en", {}).get("Product No.", ""))
    # If no explicit SKU list, use the series code
    if not skus and series:
        skus = [f"SF-{series}"]

    # Build per-page translation keys
    page_key = "p"  # scope all keys under `p.` for this page
    extra_i18n = {
        f"{page_key}.title": {lang: i18n[lang]["title"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.category": {lang: i18n[lang]["category"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.heading": {lang: i18n[lang]["desc_heading"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.description": {lang: i18n[lang]["desc_description"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.advantages": {lang: i18n[lang]["desc_advantages"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.covering": {lang: i18n[lang]["desc_covering"] for lang in ["EN", "繁", "简"]},
        f"{page_key}.applications": {lang: i18n[lang]["desc_applications"] for lang in ["EN", "繁", "简"]},
    }
    # Also include the common labels the SKU page needs
    extra_i18n.update(COMMON_LABELS)

    translations_js = build_translations_js_block(extra_i18n)

    page_title = f"{i18n['EN']['title']} — Sunfly Building Materials"
    meta_desc = (i18n["EN"]["desc_description"][0] if i18n["EN"]["desc_description"] else i18n["EN"]["title"])[:160]
    canonical = f"https://sunfly.hk/products/{CATEGORY_SLUG}/{public_slug}/"

    # ----- Body -----
    # Gallery
    if gallery:
        main_img = gallery[0]
        main_img_html = f'<img id="main-gallery-img" src="{esc(main_img["src"])}" alt="" data-i18n-alt="p.title" class="w-full h-full object-contain bg-slate-50">'
    else:
        main_img_html = '<div class="w-full h-full bg-slate-100 flex items-center justify-center text-slate-400">No image</div>'

    thumbs_html = ""
    for i, g in enumerate(gallery):
        ring = "ring-2 ring-orange-500" if i == 0 else "ring-1 ring-slate-200"
        thumbs_html += (
            f'<button type="button" onclick="document.getElementById(\'main-gallery-img\').src=\'{esc(g["src"])}\';'
            f'document.querySelectorAll(\'.gallery-thumb\').forEach(function(b){{b.classList.remove(\'ring-2\',\'ring-orange-500\');b.classList.add(\'ring-1\',\'ring-slate-200\');}});'
            f'this.classList.remove(\'ring-1\',\'ring-slate-200\');this.classList.add(\'ring-2\',\'ring-orange-500\');" '
            f'class="gallery-thumb h-20 w-20 rounded {ring} overflow-hidden flex-shrink-0 bg-slate-50">'
            f'<img src="{esc(g["src"])}" alt="" class="w-full h-full object-cover"></button>'
        )

    # Prev/next arrow overlay buttons — only shown when there are 2+ images
    if len(gallery) > 1:
        gallery_arrows_html = (
            '<button type="button" onclick="navGallery(-1)" aria-label="Previous image" '
            'class="absolute left-2 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white rounded-full w-10 h-10 flex items-center justify-center shadow-md transition-colors">'
            '<svg class="w-5 h-5 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg></button>'
            '<button type="button" onclick="navGallery(1)" aria-label="Next image" '
            'class="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white rounded-full w-10 h-10 flex items-center justify-center shadow-md transition-colors">'
            '<svg class="w-5 h-5 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
            '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></button>'
        )
    else:
        gallery_arrows_html = ""

    # Advantages / Applications: each <li> carries a data-i18n="<key>.N"
    # attribute that main.js's updateTranslations() fills in per language.
    # The list's length comes from the EN payload — padding with empty strings
    # on shorter translations is handled by build_translations_js_block().
    def render_i18n_bullets(key: str, en_items: list[str]) -> str:
        if not en_items:
            return ""
        lis = "\n".join(
            f'<li class="flex gap-2"><span class="text-orange-500 mt-1">&bull;</span>'
            f'<span data-i18n="{key}.{i}">{esc(item)}</span></li>'
            for i, item in enumerate(en_items)
        )
        return f'<ul class="space-y-2 text-slate-700">{lis}</ul>'

    advantages_list = render_i18n_bullets("p.advantages", i18n["EN"]["desc_advantages"])
    applications_list = render_i18n_bullets("p.applications", i18n["EN"]["desc_applications"])

    # Description-body image strips (overview + technical-notes sections).
    def _img_grid_html(images: list[dict]) -> str:
        if not images:
            return ""
        cells = []
        for img in images:
            src = _rewrite_img(img.get("src", ""))
            if not src or src.startswith(("http://", "https://")):
                continue
            cells.append(
                f'<figure class="rounded-lg overflow-hidden border border-slate-200 bg-slate-50">'
                f'<img src="{esc(src)}" alt="{esc(img.get("alt",""))}" loading="lazy" class="w-full h-auto object-contain">'
                f'</figure>'
            )
        if not cells:
            return ""
        return '<div class="mt-6 grid grid-cols-1 gap-4">' + "\n".join(cells) + "</div>"

    overview_media_html = _img_grid_html(desc_media_en["description"]["images"])
    covering_media_html = _img_grid_html(desc_media_en["covering"]["images"])

    # Applications: image-with-caption pairs override the plain bullet list
    # whenever the scraped HTML actually contained image/caption pairs for this
    # section. Pairs without captions (e.g. a header/diagram image at the top
    # of the section) render as standalone images — they get no i18n key so
    # they don't steal a translation slot from the captioned photos below.
    # Captioned pairs enumerate from 0 to stay aligned with desc_applications
    # (which is built from the bullet list of caption text, omitting empties).
    applications_pairs = desc_media_en["applications"]["pairs"]
    applications_gallery_html = ""
    if applications_pairs:
        cards = []
        caption_idx = 0  # running index across *captioned* pairs only
        for pair in applications_pairs:
            src = _rewrite_img(pair.get("src", ""))
            if not src or src.startswith(("http://", "https://")):
                continue
            caption_text = pair.get("caption", "").strip()
            if caption_text:
                cards.append(
                    '<figure class="rounded-lg overflow-hidden border border-slate-200 bg-white shadow-sm">'
                    f'<img src="{esc(src)}" alt="{esc(pair.get("alt",""))}" loading="lazy" class="w-full h-auto object-cover">'
                    f'<figcaption class="px-4 py-3 text-slate-700 text-sm" data-i18n="p.applications.{caption_idx}">{esc(caption_text)}</figcaption>'
                    '</figure>'
                )
                caption_idx += 1
            else:
                cards.append(
                    '<figure class="rounded-lg overflow-hidden border border-slate-200 bg-white shadow-sm">'
                    f'<img src="{esc(src)}" alt="{esc(pair.get("alt",""))}" loading="lazy" class="w-full h-auto object-cover">'
                    '</figure>'
                )
        if cards:
            applications_gallery_html = '<div class="grid grid-cols-1 md:grid-cols-2 gap-6">' + "\n".join(cards) + "</div>"

    # Description paragraphs (prose block)
    desc_paragraphs_html = "\n".join(
        f'<p class="mb-4" data-i18n="p.description.{i}"></p>'
        for i in range(len(i18n["EN"]["desc_description"]))
    )
    covering_paragraphs_html = "\n".join(
        f'<p class="mb-4" data-i18n="p.covering.{i}"></p>'
        for i in range(len(i18n["EN"]["desc_covering"]))
    )

    sku_badges_html = " ".join(
        f'<span class="inline-block bg-slate-100 text-slate-700 font-mono text-xs px-2 py-1 rounded border border-slate-200">{esc(s)}</span>'
        for s in skus
    )

    breadcrumb = f"""
    <nav class="flex flex-wrap items-center gap-2 text-sm mb-8 pb-4 border-b border-slate-200">
      <a href="/" class="text-slate-500 hover:text-orange-500 hover:underline underline-offset-2" data-i18n="nav.home"></a>
      <svg class="w-4 h-4 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
      <a href="/products/{CATEGORY_SLUG}/" class="text-slate-500 hover:text-orange-500 hover:underline underline-offset-2" data-i18n="category.title"></a>
      <svg class="w-4 h-4 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
      <span class="text-slate-900 font-semibold" data-i18n="p.title"></span>
    </nav>
    """

    primary_sku = skus[0] if skus else f"SF-{series or 'UNKNOWN'}"

    body = f"""
{render_header(active="products")}

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  {breadcrumb}

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 mb-16">
    <!-- Gallery -->
    <div>
      <div class="relative aspect-[4/3] rounded-lg overflow-hidden border border-slate-200 bg-slate-50 mb-4">
        {main_img_html}
        {gallery_arrows_html}
      </div>
      <div class="flex gap-2 flex-wrap">
        {thumbs_html}
      </div>
    </div>

    <!-- Summary + CTA -->
    <div>
      <p class="text-sm text-orange-500 font-semibold tracking-wide uppercase" data-i18n="p.category"></p>
      <h1 class="mt-2 mb-4 text-slate-900" data-i18n="p.title"></h1>
      <div class="flex flex-wrap gap-2 mb-6">
        {sku_badges_html}
      </div>

      <div class="prose max-w-none text-slate-700 mb-8">
        <p data-i18n="p.description.0"></p>
      </div>

      <div class="space-y-3 mb-8">
        <button type="button"
                onclick="addToQuote('{esc(primary_sku)}', document.querySelector('[data-i18n=\\'p.title\\']').textContent);"
                class="w-full bg-orange-500 text-white px-6 py-4 rounded hover:bg-orange-600 transition-colors font-semibold"
                data-i18n="product.addToQuote"></button>
        <button type="button" onclick="openQuoteModal()"
                class="w-full border-2 border-slate-300 text-slate-700 px-6 py-3 rounded hover:border-orange-500 hover:text-orange-500 transition-colors"
                data-i18n="product.requestQuote"></button>
      </div>
    </div>
  </div>

  <!-- Full description -->
  <section class="mb-14">
    <h2 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="product.overview"></h2>
    <div class="prose max-w-none text-slate-700">
      {desc_paragraphs_html}
    </div>
    {overview_media_html}
  </section>

  <!-- Advantages -->
  <section class="mb-14 bg-slate-50 rounded-lg p-8">
    <h2 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="product.advantages"></h2>
    {advantages_list}
  </section>

  <!-- Covering / technical notes -->
  {f'''<section class="mb-14">
    <h2 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="product.covering"></h2>
    <div class="prose max-w-none text-slate-700">
      {covering_paragraphs_html}
    </div>
    {covering_media_html}
  </section>''' if i18n["EN"]["desc_covering"] else ''}

  <!-- Applications -->
  <section class="mb-14">
    <h2 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="product.applications"></h2>
    {applications_gallery_html if applications_gallery_html else applications_list}
  </section>

  <!-- Final CTA -->
  <section class="bg-slate-900 text-white rounded-lg p-10 text-center mb-14">
    <h2 class="text-white mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="services.cta.title"></h2>
    <p class="text-slate-300 mb-6 max-w-2xl mx-auto" data-i18n="services.cta.desc"></p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <button onclick="addToQuote('{esc(primary_sku)}', document.querySelector('[data-i18n=\\'p.title\\']').textContent);"
              class="bg-orange-500 text-white px-8 py-3 rounded hover:bg-orange-600 transition-colors"
              data-i18n="product.addToQuote"></button>
      <a href="tel:+85256441916"
         class="border-2 border-white text-white px-8 py-3 rounded hover:bg-white hover:text-slate-900 transition-colors text-center"
         data-i18n="services.cta.quote"></a>
    </div>
  </section>

  <div class="mt-6">
    <a href="/products/{CATEGORY_SLUG}/" class="inline-flex items-center gap-2 text-orange-500 hover:text-orange-600">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
      <span data-i18n="product.backToCategory"></span>
    </a>
  </div>
</main>

{render_quote_modal()}
{render_footer()}
"""

    # Small JS to expand `data-i18n-list` & `data-list-fallback` at runtime.
    list_expander = r"""
<script>
(function(){
  function expandLists() {
    if (typeof translations === 'undefined' || typeof currentLanguage === 'undefined') return;
    document.querySelectorAll('[data-i18n-list]').forEach(function (ul) {
      var key = ul.getAttribute('data-i18n-list');
      var count = parseInt(translations[currentLanguage][key + '.count'] || '0', 10);
      var html = '';
      for (var i = 0; i < count; i++) {
        var txt = translations[currentLanguage][key + '.' + i] || '';
        if (txt) html += '<li class="flex gap-2"><span class="text-orange-500 mt-1">&bull;</span><span>' + txt.replace(/</g, '&lt;') + '</span></li>';
      }
      ul.innerHTML = html;
    });
    // Hide any static EN fallback that has an equivalent i18n-list version
    document.querySelectorAll('[data-list-fallback]').forEach(function(el){
      var key = el.getAttribute('data-list-fallback');
      var dyn = document.querySelector('[data-i18n-list="'+key+'"]');
      if (dyn && dyn.children.length) el.style.display = 'none';
      else el.style.display = '';
    });
  }
  // Hook: whenever changeLanguage runs, re-expand.
  var origChange = window.changeLanguage;
  window.changeLanguage = function (lang) {
    if (typeof origChange === 'function') origChange(lang);
    expandLists();
  };
  document.addEventListener('DOMContentLoaded', expandLists);

  // Gallery prev/next navigation — advances through thumbnail buttons, wrapping
  // around at either end. Relies on the thumbs' existing onclick handler to
  // swap the main image + ring styling.
  window.navGallery = function (direction) {
    var thumbs = document.querySelectorAll('.gallery-thumb');
    if (!thumbs.length) return;
    var activeIndex = 0;
    for (var i = 0; i < thumbs.length; i++) {
      if (thumbs[i].classList.contains('ring-orange-500')) { activeIndex = i; break; }
    }
    var nextIndex = (activeIndex + direction + thumbs.length) % thumbs.length;
    thumbs[nextIndex].click();
  };
})();
</script>
"""

    page_html = render_head(page_title, meta_desc, canonical, alt_langs={
        "en": canonical,
        "zh-Hant": canonical,
        "zh-Hans": canonical,
        "x-default": canonical,
    }) + body + render_body_end(translations_js, list_expander_js=list_expander)

    out_path = dest_root / "products" / CATEGORY_SLUG / public_slug / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_html, encoding="utf-8")
    return out_path


# ----- Category grid page ---------------------------------------------------

def render_category_page(products: list[dict], slugs: dict[Any, str], scrape_root: Path, dest_root: Path, skip_images: bool = False) -> Path:
    staged = []
    for p in products:
        info = stage_product_assets(p, scrape_root, dest_root, slugs[p["id"]], skip_images=skip_images)
        title_en = strip_brand(display_title(p["title"]["en"]))
        title_sc = strip_brand(display_title(p["title"]["zh"]))
        title_tc = to_zh_hk(title_sc)
        staged.append({
            "public_slug": slugs[p["id"]],
            "thumb": info["thumb"],
            "series": series_code(p["title"]["en"]),
            "title_en": title_en,
            "title_tc": title_tc,
            "title_sc": title_sc,
        })

    # i18n payload
    extra_i18n: dict[str, dict[str, str]] = {}
    extra_i18n.update(COMMON_LABELS)
    for s in staged:
        key = f"cat.{s['public_slug']}"
        extra_i18n[key] = {"EN": s["title_en"], "繁": s["title_tc"], "简": s["title_sc"]}
    translations_js = build_translations_js_block(extra_i18n)

    cards_html = ""
    for s in staged:
        slug = s["public_slug"]
        thumb = s["thumb"] or "/assets/products1.png"
        series_badge = (
            f'<span class="inline-block bg-orange-50 text-orange-600 text-xs font-mono font-semibold px-2 py-1 rounded">{esc(s["series"])}</span>'
            if s["series"] else ""
        )
        cards_html += f"""
        <a href="/products/{CATEGORY_SLUG}/{esc(slug)}/" class="group bg-white border border-slate-200 rounded-lg overflow-hidden hover:shadow-xl hover:border-orange-300 transition-all">
          <div class="aspect-[4/3] overflow-hidden bg-slate-50">
            <img src="{esc(thumb)}" alt="{esc(s["title_en"])}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
          </div>
          <div class="p-5">
            <div class="mb-2">{series_badge}</div>
            <h3 class="text-slate-900 text-base font-semibold mb-3 min-h-[3rem]" data-i18n="cat.{esc(slug)}"></h3>
            <span class="text-orange-500 text-sm font-semibold flex items-center gap-1" data-i18n="category.viewDetails"></span>
          </div>
        </a>
        """

    body = f"""
{render_header(active="products")}

<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <nav class="flex flex-wrap items-center gap-2 text-sm mb-8 pb-4 border-b border-slate-200">
    <a href="/" class="text-slate-500 hover:text-orange-500 hover:underline underline-offset-2" data-i18n="nav.home"></a>
    <svg class="w-4 h-4 text-slate-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
    <span class="text-slate-900 font-semibold" data-i18n="category.title"></span>
  </nav>

  <header class="mb-10 max-w-3xl">
    <h1 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="category.title"></h1>
    <p class="text-slate-600 text-lg" data-i18n="category.subtitle"></p>
  </header>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {cards_html}
  </div>
</main>

{render_quote_modal()}
{render_footer()}
"""

    canonical = f"https://sunfly.hk/products/{CATEGORY_SLUG}/"
    page_html = render_head(
        f"{CATEGORY_I18N['EN']} — Sunfly Building Materials",
        "Browse our full range of anti-static and ventilation access floor systems for computer rooms, data centers and control rooms.",
        canonical,
        alt_langs={"en": canonical, "zh-Hant": canonical, "zh-Hans": canonical, "x-default": canonical},
    ) + body + render_body_end(translations_js)

    out_path = dest_root / "products" / CATEGORY_SLUG / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_html, encoding="utf-8")
    return out_path


# ----- Hub stub page --------------------------------------------------------

def render_hub_page(dest_root: Path) -> Path:
    extra_i18n = {
        **COMMON_LABELS,
        "hub.subtitle": {
            "EN": "Our building-materials catalog. Right now we have detailed product pages for access flooring; the rest of the range (ceilings, glazing, steel framing) is coming soon — contact us for quotations in the meantime.",
            "繁": "我們的建築材料目錄。目前架空地板系列已有完整產品頁面，其他系列（天花、玻璃、輕鋼架）即將推出，歡迎先聯絡我們索取報價。",
            "简": "我们的建筑材料目录。目前架空地板系列已有完整产品页面，其他系列（天花、玻璃、轻钢架）即将推出，欢迎先联系我们索取报价。",
        },
    }
    translations_js = build_translations_js_block(extra_i18n)
    canonical = "https://sunfly.hk/products/"

    tiles = [
        {
            "href": f"/products/{CATEGORY_SLUG}/",
            "img": "/assets/products1.png",
            "name_key": "products.raisedFloor.name",
            "desc_key": "products.raisedFloor.desc",
            "available": True,
        },
        {"href": "/#products", "img": "/assets/products2.png", "name_key": "products.ceiling.name", "desc_key": "products.ceiling.desc", "available": False},
        {"href": "/#products", "img": "/assets/products3.jpeg", "name_key": "products.glazing.name", "desc_key": "products.glazing.desc", "available": False},
        {"href": "/#products", "img": "/assets/products4.jpeg", "name_key": "products.steelFraming.name", "desc_key": "products.steelFraming.desc", "available": False},
    ]
    cards = ""
    for t in tiles:
        badge = ""
        if not t["available"]:
            badge = '<span class="inline-block bg-slate-100 text-slate-500 text-xs px-2 py-1 rounded mb-2">Coming soon</span>'
        else:
            badge = '<span class="inline-block bg-orange-100 text-orange-600 text-xs font-semibold px-2 py-1 rounded mb-2">Browse catalog</span>'
        cards += f"""
        <a href="{t['href']}" class="group bg-white border border-slate-200 rounded-lg overflow-hidden hover:shadow-xl hover:border-orange-300 transition-all">
          <div class="aspect-[4/3] overflow-hidden bg-slate-50">
            <img src="{t['img']}" alt="" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
          </div>
          <div class="p-5">
            {badge}
            <h3 class="text-slate-900 mb-2" data-i18n="{t['name_key']}"></h3>
            <p class="text-slate-600 text-sm" data-i18n="{t['desc_key']}"></p>
          </div>
        </a>
        """

    body = f"""
{render_header(active="products")}
<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
  <header class="mb-10 max-w-3xl">
    <h1 class="text-slate-900 mb-6 pb-2 inline-block border-b-4 border-orange-500" data-i18n="nav.products"></h1>
    <p class="text-slate-600 text-lg" data-i18n="hub.subtitle"></p>
  </header>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
    {cards}
  </div>
</main>
{render_quote_modal()}
{render_footer()}
"""
    canonical_hub = canonical
    page_html = render_head("Products — Sunfly Building Materials", "Premium building materials: access floor systems, ceilings, glazing and light-steel framing for overseas buyers.", canonical_hub) + body + render_body_end(translations_js)
    out = dest_root / "products" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page_html, encoding="utf-8")
    return out


# ----- Main -----------------------------------------------------------------

def flatten_products(data: dict) -> list[dict]:
    out: list[dict] = []
    for k in ["hot_products", "new_products"]:
        cat = data["categories"].get(k) or {}
        for p in cat.get("products", []):
            out.append(p)
    # Dedup by id just in case
    seen: set[Any] = set()
    unique: list[dict] = []
    for p in out:
        if p["id"] in seen:
            continue
        seen.add(p["id"])
        unique.append(p)
    return unique


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=str(REPO_ROOT_DEFAULT))
    ap.add_argument("--only-slug", default=None, help="If set, only generate this one SKU page (plus the hub + category).")
    ap.add_argument("--skip-images", action="store_true", help="Skip image copy (faster re-runs while iterating on HTML).")
    ap.add_argument("--skip-hub", action="store_true")
    ap.add_argument("--skip-category", action="store_true")
    args = ap.parse_args()

    site_root = Path(args.site_root)
    scrape_root = site_root / "parete-scrape"
    products_json = scrape_root / "products.json"
    if not products_json.exists():
        sys.exit(f"products.json not found at {products_json}")

    data = json.loads(products_json.read_text(encoding="utf-8"))
    products = flatten_products(data)
    print(f"[build] loaded {len(products)} products from {products_json}")

    slugs = assign_public_slugs(products)
    # Report the slug map so Yifan can eyeball it
    print("[build] public slug map:")
    for p in products:
        print(f"    {p['id']:>3}  {slugs[p['id']]:<35}  {p['title']['en'][:60]}")

    # Hub page removed 2026-04-23 — home-page cards now link directly to
    # each category page (or carry a "coming soon" badge). The
    # render_hub_page() function is retained for reference but not invoked.
    # Pass --skip-hub is now implicit. Use --build-hub to re-enable.
    if getattr(args, "build_hub", False):
        out = render_hub_page(site_root)
        print(f"[build] wrote {out.relative_to(site_root)}")

    # Category grid
    if not args.skip_category:
        out = render_category_page(products, slugs, scrape_root, site_root, skip_images=args.skip_images)
        print(f"[build] wrote {out.relative_to(site_root)}")

    # SKU pages
    target_products: list[dict]
    if args.only_slug:
        target_products = [p for p in products if p["slug"] == args.only_slug]
        if not target_products:
            sys.exit(f"no product with slug={args.only_slug}")
    else:
        target_products = products

    for p in target_products:
        out = render_sku_page(p, scrape_root, site_root, slugs[p["id"]], skip_images=args.skip_images)
        print(f"[build] wrote {out.relative_to(site_root)}")


if __name__ == "__main__":
    main()
