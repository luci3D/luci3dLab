# The website

Plain HTML, CSS and a little JavaScript: no build step. The colours come from `brand/palette/luci3d.gpl`.

| Page | File |
|---|---|
| Home | `index.html` |
| Open DVR | `dvr.html` |
| Shop | `shop.html` (cards come from `js/products.js`) |
| Zine maze game | `game.html` + `js/maze.js` |

## Preview on your computer

The maze reads image pixels, which browsers only allow over http, so serve the folder instead of double-clicking the files:

```bash
cd site
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Common edits

- **Products, prices and buy buttons:** `js/products.js`. When a product is ready, set its `status` to `"available"`, fill in `price`, and paste its Stripe Payment Link into `stripe` and its PayPal link into `paypal`. The buttons appear by themselves.
- **"Get notified" link:** `NOTIFY_URL` at the bottom of `js/products.js` (a newsletter sign-up page, once there is one).
- **Company name:** search all `.html` files for `luci3D hardware`.
- **YouTube link:** the `TODO` in the footer of each page.
- **Art:** after re-rendering anything in `art/`, run `python3 site/tools/sync_assets.py` to copy it into `site/img/` (it also rebuilds the favicon).

## Publishing (GitHub Pages)

`.github/workflows/pages.yml` publishes this folder on every push to `main` that changes it. Turn it on once: repo **Settings → Pages → Build and deployment → Source: GitHub Actions**. The site then lives at `https://luci3d.github.io/luci3dlab/` until a custom domain is set (Settings → Pages → Custom domain).
