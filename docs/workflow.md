# Workflow: brand → website + shop → game

## Tools

- **Aseprite** (owner's computer) for drawing and polishing.
- **Scripts in this repo** for anything procedural: palettes, logo, PCB scenes, tilesets, exports. Art starts as code, gets repainted in Aseprite, and the PNGs come back into the repo.
- **No PixelLab for now.** Reconsider for one month when the game needs many animated characters.

## Steps

| # | Step | Status |
|---|---|---|
| 0 | Style and sizes: top-down 3/4, flat/no outlines, 32 px humans, 480×270 screen, palette | Done (see README) |
| 1 | Brand kit: palette, logo, wordmark, pixel font, story | Palette, logo and story in; wordmark and font to do |
| 1b | The Stack: mock-up → tileset (roads, chips, pads, vias, grime overlays) | Mock-up v1 in `art/world/` |
| 2 | Website: home (animated FC city), open-dvr, shop, game teaser, links, email sign-up | Next |
| 3 | Shop: Stripe Payment Links (no monthly fee) + PayPal | Waiting on: where the business is registered |
| 4 | YouTube kit: profile 800×800, banner 2560×1440, intro animation (thumbnails are designed separately) | After the site |
| 5 | Game: vertical slice built from the zine mazes and the FC city tiles | After the site |

## Shop notes

- No custom cart. Stripe Payment Links: one link per product, collects the shipping address, card fees only.
- PayPal: if the business is in the EEA, UK or Switzerland, Stripe can offer PayPal inside the same checkout (enable it under Payment methods in the Stripe dashboard). Elsewhere, add a separate PayPal button next to the Stripe one.
- Before the first sale: tax/VAT and electronics rules (CE in Europe, FCC in the US) for the countries you ship to.
- Hosting: GitHub Pages or Cloudflare Pages (free). Buy a domain once the name is settled.
