/* The shop's product list. Edit this file to add products or switch them on.

   status:  "planned"     on the roadmap, no buy buttons
            "prototype"   boards exist, not for sale yet ("Get notified")
            "available"   for sale: shows the buy buttons below
   price:   text shown on the card, e.g. "CAD 39". Leave "" to hide.
   stripe:  a Stripe Payment Link (dashboard.stripe.com > Payment Links), e.g. "https://buy.stripe.com/..."
   paypal:  a PayPal payment link or button link from your PayPal Business account
   image:   a file in site/img/, or "" for the placeholder
*/
window.PRODUCTS = [
  {
    id: "decoder-board",
    name: "open-dvr decoder board",
    version: "v0.2",
    status: "prototype",
    price: "",
    stripe: "",
    paypal: "",
    image: "",
    summary: "Turns your analog FPV camera's video into MIPI CSI-2 for a Luckfox Pico, and carries the DVR's microphone. The heart of the DIY DVR kit.",
    points: ["TP9950 video decoder, real 50/60 fps field capture", "MEMS microphone for in-sync audio", "Taps the camera line in parallel: zero added latency", "Open hardware: KiCad files, Gerbers and BOM on GitHub"],
    link: "https://github.com/luci3D/open-dvr/tree/main/decoder-board",
  },
  {
    id: "imu-breakout",
    name: "IMU breakout",
    version: "",
    status: "planned",
    price: "", stripe: "", paypal: "", image: "",
    summary: "A gyro board for the DVR: logs the quad's motion next to every clip, ready for Gyroflow stabilisation.",
    points: ["LSM6DSOX IMU", "Gyroflow-ready .gcsv logs"],
    link: "dvr.html#roadmap",
  },
  {
    id: "dvr-20",
    name: "On-quad DVR, 20 x 20",
    version: "",
    status: "planned",
    price: "", stripe: "", paypal: "", image: "",
    summary: "Everything on one board: recorder, video decoder, IMU and mic, in a 20 x 20 mm stack mount.",
    points: ["Rockchip RV1103", "Same open recorder software"],
    link: "dvr.html#roadmap",
  },
  {
    id: "dvr-whoop",
    name: "On-quad DVR, whoop",
    version: "",
    status: "planned",
    price: "", stripe: "", paypal: "", image: "",
    summary: "The same circuit on the smallest board we can make, for whoops and micros.",
    points: ["Smallest possible footprint"],
    link: "dvr.html#roadmap",
  },
];

/* Where "Get notified" goes. Set to your newsletter sign-up page once you have one. */
window.NOTIFY_URL = "https://github.com/luci3D/open-dvr";
