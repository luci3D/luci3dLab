# Website to-do

The site: https://luci3d.github.io/luci3dLab/ (source in [`../site/`](../site/), how to edit it in [`../site/README.md`](../site/README.md)).
Tick items off here as they're done. **You** = only you can do it (accounts, money, decisions). **Claude** = I can do it once you say go.

## Done

- [x] Pages: home, open-dvr, the Lab (shop), zine maze game, font test page (`fonts.html`, not linked)
- [x] Live on GitHub Pages; every push to `main` publishes in a minute or two
- [x] Fonts: Silkscreen headings, Doto (dot matrix) body text
- [x] Browsers load fresh CSS/JS after every publish (no stale fonts)
- [x] Email sign-up form built on the Lab page (waiting for a newsletter account, see below)
- [x] Company name: **Tracewinder Labs** (sidewinder snake, winding traces, wound motor coils)

## 1. Domain and email (do in this order)

Each step needs the one before it.

1. [x] **Decide the company name** (You): **Tracewinder Labs**
2. [ ] **Buy the domain** (You): **`tracewinder.io`** as the main address. All of these were unregistered when checked on 2026-11-27: tracewinder.io / .com / .ca / .net / .dev, and the same with tracewinderlabs.
   - [ ] Also register **`tracewinder.com`** and **`tracewinder.ca`** and point them at the .io (people type .com by habit, .ca says Canadian, and it stops anyone else taking them)
   - [ ] Check "Tracewinder" in the trademark databases first: CIPO (Canada) and USPTO (US)
   - [ ] Grab the handles while they're free: YouTube, Instagram, GitHub (`tracewinder` or `tracewinderlabs`)
3. [ ] **Point the domain at the website** (You, with Claude's checklist)
   - [ ] In GitHub: Settings → Pages → **Custom domain**, enter it, then tick **Enforce HTTPS** once the certificate is issued
   - [ ] In GitHub: verify the domain under your account's Settings → Pages (stops anyone else claiming it)
   - [ ] DNS records at the registrar: the four GitHub Pages `A` records for the bare domain and a `www` `CNAME` to `luci3d.github.io` (Claude writes the exact list when the domain exists)
   - [ ] Claude: switch the site's links and social-preview image to the new address, and check it loads
4. [ ] **Mailbox on the domain**, e.g. `hello@tracewinder.io` (You). Pick one: Zoho Mail, Fastmail, Google Workspace or Proton Mail.
   - [ ] Add the provider's DNS records: MX (receiving), SPF and DKIM (so your mail isn't spam), DMARC
   - [ ] Optional: extra addresses (`orders@`, `support@`) forwarding into the same inbox, e.g. Cloudflare Email Routing
5. [ ] **Newsletter account** for the "Get notified" list (You). Buttondown is wired in; Mailchimp, MailerLite or Kit also work.
   - [ ] Keep **double opt-in** on (subscribers confirm by email; what Canada's anti-spam law, CASL, expects)
   - [ ] Sender name "Tracewinder Labs", reply-to your mailbox
   - [ ] Mailing address in the email footer (CASL requires one; a PO box works)
   - [ ] Send Claude the username (or the form address from another service)
6. [ ] **Switch the sign-up on** (Claude): set `NOTIFY.action` in `site/js/products.js`, then a real test sign-up with your address
7. [ ] **Send newsletters from your domain** (You, with Claude's checklist): add Buttondown's sending-domain DNS records so launch emails come from `hello@tracewinder.io`
8. [ ] **Put the email address on the site** (Claude): footer, Lab questions, a contact line

## 2. Before the DIY kit goes on sale

- [ ] Tested numbers for the kit: resolution, frame rate, largest SD card (You). Claude replaces the asterisked specs in `site/js/products.js`
- [ ] Kit photos (You). Claude adds them to the product card
- [ ] Price (You)
- [ ] Stripe account and a Payment Link for the kit (You)
- [ ] PayPal Business account and a payment link (You; Stripe can't offer PayPal to Canadian businesses)
- [ ] Claude: switch the kit to "available" with both buy buttons, test them
- [ ] Shipping: carrier, rates, which countries (You)
- [ ] Taxes: GST/HST registration (required past CAD 30,000 in sales over four quarters), US sales tax and duties (You, maybe an accountant)
- [ ] Electronics rules for bare boards and kits where you ship: ISED (Canada), FCC (US), CE (EU) (You)
- [ ] Policy pages: privacy (needed once you collect emails), shipping and returns, warranty (You decide, Claude drafts)

## 3. Content and polish

- [ ] YouTube channel link in the footer (You send it, Claude adds it)
- [ ] Read all the page text and change anything that doesn't sound like you (You)
- [ ] **Rename to Tracewinder Labs** (Claude): site header, footer, page titles and descriptions, the Lab copy, the story doc and READMEs. The snake logo stays; luci3D remains the snake's name in the lore and your pilot handle
- [ ] A Tracewinder Labs wordmark next to the snake, in the site's pixel style (Claude drafts, You choose)
- [ ] Social-preview image with a full web address, so links shared on Discord, Reddit and so on show a picture (Claude, after the domain)
- [ ] A 404 page in the site's style (Claude)
- [ ] Phone home-screen icon (Claude)
- [ ] Visitor stats, optional: a privacy-friendly option such as Cloudflare Web Analytics (You decide)
- [ ] Update the publish workflow's GitHub Actions to newer versions (the Node.js 20 warning) (Claude)
- [ ] Keep or remove the font test page (You decide)
- [ ] open-dvr repo: reword the roadmap line about releasing Gerbers and BOM (You decide)

## Later

- [ ] The game: rework the scenes and characters, then a playable demo on the Game page
