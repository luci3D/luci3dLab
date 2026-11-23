# Workflow: brand → website + shop → game

## Tools

- **Aseprite** (owner's computer) for drawing and polishing.
- **Scripts in this repo** for anything procedural: palettes, logo, PCB scenes, tilesets, exports. Art starts as code, gets repainted in Aseprite, and the PNGs come back into the repo.
- **No PixelLab for now.** Reconsider for one month when the game needs many animated characters.

## Steps

| # | Step | Status |
|---|---|---|
| 0 | Style and sizes: flat/no outlines, black boards, city view in perspective, street view top-down with 32 px humans | Done (see README) |
| 1 | Brand kit: palette, logo, wordmark, pixel font, story | Palette, logo and story in; wordmark and font to do |
| 1b | The Stack: city view (perspective) → street-view tileset (roads, chips, pads, vias, grime overlays) | City view v2 in `art/world/` |
| 1c | Characters: 5 guild creatures with weapons (32 px), luci3D the snake as a pet | Front-view drafts in `art/sprites/`; next: other facings, walk and attack frames |
| 2 | Website: home (animated FC city), open-dvr, shop, game teaser, links, email sign-up | Next |
| 3 | Shop: Stripe Payment Links (no monthly fee) + a separate PayPal button | Business: Canada |
| 4 | YouTube kit: profile 800×800, banner 2560×1440, intro animation (thumbnails are designed separately) | After the site |
| 5 | Game: vertical slice built from the zine mazes and the FC city tiles | After the site |

## Shop notes

The business is registered in Canada.

- No custom cart. Stripe Payment Links: one link per product, collects the shipping address, card fees only.
- PayPal: Stripe only offers PayPal inside its checkout to businesses in the EU, UK, Norway, Liechtenstein and Switzerland, not Canada. So each product gets a separate PayPal button (PayPal Business account) next to the Stripe one. Two dashboards to check for orders.
- Before the first sale, check:
  - GST/HST: registration is optional until sales pass the CRA's small-supplier threshold (CAD 30,000 over four consecutive quarters).
  - Shipping to the US: US state sales tax and import duties.
  - Electronics rules for bare boards and kits in the countries you ship to (ISED in Canada, FCC in the US, CE in Europe).
- Hosting: GitHub Pages or Cloudflare Pages (free). Buy a domain once the name is settled.
