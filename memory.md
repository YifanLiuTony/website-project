# Project Memory

## Scope
- This repo is the Sunfly building materials marketing site used to gather leads.
- It supports 3 languages: English (`EN`), Traditional Chinese / Hong Kong (`繁`), and Simplified Chinese (`简`).
- Ignore everything under `zkya/`; it belongs to a different project.

## Current Site Shape
- The main site is a mostly static HTML site, not a framework app.
- Core shared files:
  - `/Users/yifanliu/Desktop/Projects/website-project/index.html`
  - `/Users/yifanliu/Desktop/Projects/website-project/js/main.js`
  - `/Users/yifanliu/Desktop/Projects/website-project/js/translations.js`
- The homepage already has multilingual content blocks, product cards, job references, services, and a contact form powered by EmailJS in `js/main.js`.
- The homepage links product entry points to `/products/`.

## Product Content Pipeline
- Product detail content was scraped from `https://www.parete.net/`.
- Scraped source data lives in:
  - `/Users/yifanliu/Desktop/Projects/website-project/parete-scrape/products.json`
  - `/Users/yifanliu/Desktop/Projects/website-project/parete-scrape/images/`
- `products.json` contains 24 products total:
  - 12 in `hot_products`
  - 12 in `new_products`
- Generator script:
  - `/Users/yifanliu/Desktop/Projects/website-project/tools/build_products.py`
- Focused live-fetch/update script:
  - `/Users/yifanliu/Desktop/Projects/website-project/tools/fetch_parete_product.py`
- The generator now outputs:
  - `/products/index.html`
  - `/products/<slug>/index.html`
  - mirrored product images under `/assets/products/<slug>/`

## Generator Rules / Assumptions
- User-facing product pages remove Parete branding and replace it with Sunfly wording where needed.
- `PRT-` SKU prefixes are rewritten to `SF-`.
- Commercial info like price, MOQ, delivery, payment terms, packing, and supply ability is intentionally hidden from public HTML and routed through quote requests instead.
- Traditional Chinese content is derived from Simplified Chinese with OpenCC conversion in the generator.
- The generator includes quote-cart / quote-modal UI and page-level translations directly inside generated product pages.

## Current Product Page Status
- The product area was refactored to skip middle category URLs.
- Public URL model:
  - `/products/` is the unified catalog page.
  - `/products/<public-slug>/` is each product detail page.
- `/products/index.html` groups the 24 scraped products under one parent product family:
  - Raised Floor System
- Inside Raised Floor System, the page uses collapsible browsing sections:
  - Steel Anti-Static Access Floors
  - Calcium Sulphate Access Floors
  - Aluminum Access Floors
  - OA / Network Raised Floors
  - Ventilation Access Floors
- This parent-family structure is intentional so future product families such as ceiling, glazing, and steel framing can be added alongside Raised Floor System later.
- Detail pages were generated for all 24 public slugs, e.g. `/products/af-1/`, `/products/vf-3/`, and `/products/c4-oa-600-stringer/`.
- The older `/products/anti-static-access-floor/` output still exists in the tree as an obsolete generated page from the previous structure; new generated links should not point there.
- The stray `/products/index 2.html` also still exists as an old draft/generated hub and should eventually be removed or reconciled.

## AF-1 Detail Page Pattern
- `/Users/yifanliu/Desktop/Projects/website-project/products/af-1/index.html` is the current generated reference implementation.
- Structure already includes:
  - breadcrumb
  - product gallery
  - overview / description
  - advantages
  - technical notes / covering section
  - applications with images
  - quote CTA and floating quote cart
  - inline translations for EN / 繁 / 简
- The same generated template has now been rolled across the rest of the scraped product catalog.

## Assets / Repo State
- The repo currently has a very large staged/untracked content import centered on `parete-scrape/` and `assets/products/`.
- The scraped images and mirrored product assets appear far more complete than the checked-in HTML pages.
- This suggests the data ingestion and asset mirroring work is ahead of the final page-generation / cleanup / commit decisions.

## Things To Watch
- `products/index 2.html` is likely a temporary or accidental filename and should eventually be removed if no longer needed.
- `products/anti-static-access-floor/` is obsolete under the new URL model and should eventually be removed or redirected if desired.
- The homepage JSON-LD in `index.html` appears to have malformed JSON in some `Offer` objects because of missing commas before `"price"` fields.
- The site mixes shared global translations (`js/translations.js`) with page-local generated translations inside product pages.
- `tools/build_products.py` currently depends on OpenCC (`opencc-python-reimplemented`).
- The script default `REPO_ROOT_DEFAULT` points to an old session path and should not be trusted unless `--site-root` is passed or the script is updated.
- AF-2 was tested as a live Parete fetch case. The live Parete ZH page reuses mostly English body copy, so `tools/fetch_parete_product.py` is designed to preserve existing normalized Chinese description text when the live ZH body has little/no CJK content.
- The AF-2 fetch verification result was: 6 EN gallery images, 6 ZH gallery images, 11 EN body images, 11 ZH body images, 5 specs per language, no missing local image files, and no absolute `/upload` image paths in generated `/products/af-2/`.

## Best Resume Point
- Continue polishing `/products/` as the grouped catalog and `/products/af-1/` as the reference detail page.
- Clean up obsolete product outputs (`products/index 2.html`, `products/anti-static-access-floor/`) once the new route structure is accepted.
- Confirm the quote flow works consistently across homepage, product catalog, and detail pages.
