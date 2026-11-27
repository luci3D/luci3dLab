# The website

Plain HTML, CSS and a little JavaScript: no build step. The colours come from `brand/palette/luci3d.gpl`.

| Page | File |
|---|---|
| Home | `index.html` |
| Open DVR | `dvr.html` |
| The Lab (shop) | `shop.html` (cards come from `js/products.js`) |
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
- **Email sign-up ("Get notified"):** the form is on the Lab page (`shop.html#notify`), and every "Get notified" button leads there. It posts straight to the newsletter service. Turn it on by setting `NOTIFY.action` at the bottom of `js/products.js` (for Buttondown: `https://buttondown.com/api/emails/embed-subscribe/YOUR-USERNAME`). Until then it shows "Sign-up opens soon".
- **Fonts:** Silkscreen for headings, menu and buttons; Doto (dot matrix, weight 900) for everything else (`--font-silk` and `--font-body` in `css/style.css`). `fonts.html` (not linked) compares pixel fonts on real page content.
- **Company name:** search all `.html` files for `Tracewinder Labs`.
- **YouTube link:** the `TODO` in the footer of each page.
- **Art:** after re-rendering anything in `art/`, run `python3 site/tools/sync_assets.py` to copy it into `site/img/` (it also rebuilds the favicon).

## Publishing (GitHub Pages)

Links to `css/` and `js/` files end in `?v=dev`; the publish step swaps that for the commit ID, so browsers load the new files after every deploy instead of reusing old ones. Keep the `?v=dev` on any new stylesheet or script link.


`.github/workflows/pages.yml` publishes this folder on every push to `main` that changes it. Turn it on once: repo **Settings → Pages → Build and deployment → Source: GitHub Actions**. The site then lives at `https://luci3d.github.io/luci3dlab/` until a custom domain is set (Settings → Pages → Custom domain).
