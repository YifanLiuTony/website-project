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
- The stray `/products/index 2.html` old draft/generated hub was removed.

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

## Product Image URL Branding Inventory (2026-05-25)
- Scope: the 317 source image files under `/Users/yifanliu/Desktop/Projects/website-project/parete-scrape/images/`. Do not separately count `/assets/products/`, because `tools/build_products.py` mirrors the scrape-source images into that public asset tree.
- The user confirmed that these public-source images may be used and edited. Cleanup is limited to visible email/URL marks; central `PARETE` logo watermarks are intentionally ignored.
- Per-file treatment manifest: `/Users/yifanliu/Desktop/Projects/website-project/parete-scrape/image-url-branding-inventory.csv`.
- Inventory groups:

| Group | Files | Recommended Later Treatment |
| --- | ---: | --- |
| `easy_footer_crop_or_cover` | 104 | All `*thickbox*` source images use the removable gray footer containing `export@parete.net`; crop the footer or cover it with the adjacent footer color. |
| `bottom_url_mask_candidate` | 162 | OCR detected a URL entirely within the bottom 15% of the image, usually `www.parete.net` in a corner; mask or narrowly crop after a visual check. |
| `manual_review` | 51 | No URL matched automatically; do not assume clean because spot checks found small or low-contrast URL marks that OCR can miss. |

- Representative easy footer crop files: `images/24-steel-access-floor-pvc/24-248-thickbox_steel-access-floor-pvc.jpg`, `images/25-steel-access-floor-ceramic/25-269-thickbox_steel-access-floor-ceramic.jpg`, and `images/51-c5-0a-500-low-height-raised-floor-with-trucks/51-369-thickbox_c5-0a-500-low-height-raised-floor-with-trucks.jpg`.
- Representative narrow-mask candidates: `images/25-steel-access-floor-ceramic/images_05-steel-ceramic-01.jpg`, `images/40-steel-ventilation-access-floor/images_steel_ventilation_floor-vf1-21-3.jpg`, and `images/shared/images_01-steel_hpl.png`.
- When processing later, change files in `parete-scrape/images/` first and regenerate or re-stage `assets/products/`; editing only the mirrored public assets will be overwritten on a future product build.

## Things To Watch
- `products/anti-static-access-floor/` is obsolete under the new URL model and should eventually be removed or redirected if desired.
- The homepage JSON-LD in `index.html` appears to have malformed JSON in some `Offer` objects because of missing commas before `"price"` fields.
- The site mixes shared global translations (`js/translations.js`) with page-local generated translations inside product pages.
- `tools/build_products.py` currently depends on OpenCC (`opencc-python-reimplemented`).
- The script default `REPO_ROOT_DEFAULT` points to an old session path and should not be trusted unless `--site-root` is passed or the script is updated.
- AF-2 was tested as a live Parete fetch case. The live Parete ZH page reuses mostly English body copy, so `tools/fetch_parete_product.py` is designed to preserve existing normalized Chinese description text when the live ZH body has little/no CJK content.
- The AF-2 fetch verification result was: 6 EN gallery images, 6 ZH gallery images, 11 EN body images, 11 ZH body images, 5 specs per language, no missing local image files, and no absolute `/upload` image paths in generated `/products/af-2/`.

## Best Resume Point
- Continue polishing `/products/` as the grouped catalog and `/products/af-1/` as the reference detail page.
- Clean up obsolete product outputs (`products/anti-static-access-floor/`) once the new route structure is accepted.
- Confirm the quote flow works consistently across homepage, product catalog, and detail pages.
