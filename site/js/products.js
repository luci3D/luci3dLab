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

/* Where "Get notified" goes. Set to your newsletter sign-up page once you have one. */
window.NOTIFY_URL = "https://github.com/luci3D/open-dvr";
