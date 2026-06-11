# AGENTS.md

## Repository Context

- This is the Sunfly building materials marketing site and static product catalog.
- The main site is mostly static HTML, CSS, and JavaScript.
- Core shared files include `index.html`, `js/main.js`, and `js/translations.js`.
- Product source data and assets live under `parete-scrape/`; generated public product pages live under `products/` and mirrored assets under `assets/products/`.
- Treat `zkya/` as a different project unless the user explicitly asks to work there.

## Working Agreements

- Inspect the current workspace before deciding what to change; local project memory is context, but current files are the source of truth.
- For complex implementations, present a plan and wait for approval before changing files.
- Keep edits scoped to the requested behavior and preserve unrelated user changes in the worktree.
- Keep public pages branded for Sunfly. Remove or rewrite Parete-facing branding in rendered public content.
- Do not expose commercial supplier details such as price, MOQ, packing, production, delivery, payment, or supply terms in public HTML unless the user explicitly asks.

## Website Workflow

- For product-page changes, prefer updating `tools/build_products.py` or `parete-scrape/products.json` before editing generated product HTML directly.
- Pass `--site-root /Users/yifanliu/Desktop/Projects/website-project` when running product-generation scripts if there is any doubt about the working directory.
- When cleaning product image branding, update source images under `parete-scrape/images/` first, then regenerate or restage mirrored files under `assets/products/`.
- Check multilingual behavior for English, Traditional Chinese / Hong Kong, and Simplified Chinese when changing visible site copy.

## Validation

- For generator changes, run the focused product build command when feasible, for example `python3 tools/build_products.py --site-root /Users/yifanliu/Desktop/Projects/website-project --only-slug <slug>`.
- For user-facing layout changes, verify the rendered page in a browser or with screenshots.
- If validation cannot be run, report the exact blocker and the command or page that should be checked next.
