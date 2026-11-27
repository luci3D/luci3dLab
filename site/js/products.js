/* The Lab's product list. Edit this file to add products or switch them on.

   status:  "prototype"   boards exist, not for sale yet ("Get notified")
            "available"   for sale: shows the buy buttons below
            "planned"     on the roadmap, no buttons
   price:   text shown on the card, e.g. "CAD 59". Leave "" to hide.
   stripe:  a Stripe Payment Link (dashboard.stripe.com > Payment Links), e.g. "https://buy.stripe.com/..."
   paypal:  a PayPal payment link from your PayPal Business account
   image:   a file in site/img/, or "" for the placeholder
   specs:   [label, value] rows; note: small print under them
*/
window.PRODUCTS = [
  {
    id: "diy-kit",
    name: "open-dvr DIY kit",
    version: "",
    status: "prototype",
    price: "",
    stripe: "",
    paypal: "",
    image: "",
    summary: "Our decoder board turns a Luckfox Pico Pro or Max into an analog DVR. It taps your camera line in parallel, so it never touches your live feed.",
    specs: [
      ["PAL", "960 x 576 at 50 fps*"],
      ["NTSC", "960 x 480 at 59.94 fps*"],
      ["Audio", "On-board MEMS microphone, in sync with the video"],
      ["Storage", "microSD in the Luckfox, up to 512 GB*"],
      ["Input", "Analog camera, PAL or NTSC detected automatically"],
      ["Power", "5 V from your flight controller"],
      ["You add", "A Luckfox Pico Pro or Max and a microSD card"],
    ],
    note: "* What our 0.9 recorder does today. Final numbers once the kit is tested.",
    link: "dvr.html#next",
  },
];

/* "Get notified" opens the sign-up form on the Lab page. */
window.NOTIFY_URL = "shop.html#notify";

/* The sign-up form. Fill in `action` once your newsletter account exists; until then the form
   shows "Sign-up opens soon" and sends nothing.
     action: the service's form address. Buttondown: "https://buttondown.com/api/emails/embed-subscribe/YOUR-USERNAME"
     field:  the name the service expects for the email box ("email" for Buttondown)
     extra:  hidden fields sent with it (Buttondown files the sign-up under this tag) */
window.NOTIFY = { action: "", field: "email", extra: { tag: "diy-kit" } };
