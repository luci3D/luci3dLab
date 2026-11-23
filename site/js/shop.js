/* Renders window.PRODUCTS into any element with data-products.
   data-products="all" shows every product; a number shows that many. */
(function () {
  const LABEL = { planned: "PLANNED", prototype: "PROTOTYPE", available: "IN STOCK" };

  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") n.className = v; else n.setAttribute(k, v);
    }
    for (const k of kids) if (k != null) n.append(k);
    return n;
  }

  function card(p) {
    const media = p.image
      ? el("img", { src: "img/" + p.image, alt: p.name, loading: "lazy" })
      : el("div", { class: "placeholder" }, el("img", { class: "pixel", src: "img/logo-1x.png", alt: "" }));
    const buttons = el("div", { class: "btns" });
    if (p.status === "available" && (p.stripe || p.paypal)) {
      if (p.stripe) buttons.append(el("a", { class: "btn", href: p.stripe, rel: "noopener" }, "Buy with card"));
      if (p.paypal) buttons.append(el("a", { class: "btn ghost", href: p.paypal, rel: "noopener" }, "PayPal"));
    } else if (p.status === "prototype") {
      buttons.append(el("a", { class: "btn", href: window.NOTIFY_URL || "#" }, "Get notified"));
    } else {
      buttons.append(el("span", { class: "btn", "aria-disabled": "true" }, "Coming later"));
    }
    if (p.link) buttons.append(el("a", { class: "btn ghost", href: p.link }, "Details"));
    const pts = el("ul", { class: "ticks" }, ...(p.points || []).map((t) => el("li", {}, t)));
    const specs = (p.specs || []).length
      ? el("table", { class: "specs" }, ...p.specs.map(([k, v]) => el("tr", {}, el("th", {}, k), el("td", {}, v))))
      : null;
    const note = p.note ? el("p", { class: "note" }, p.note) : null;
    return el("article", { class: "card product" },
      media,
      el("span", { class: "status " + p.status }, LABEL[p.status] || p.status.toUpperCase()),
      el("h3", {}, p.name + (p.version ? " " + p.version : "")),
      p.price ? el("p", { class: "price" }, p.price) : null,
      el("p", {}, p.summary),
      p.points ? pts : null,
      specs,
      note,
      buttons);
  }

  document.querySelectorAll("[data-products]").forEach((root) => {
    const n = root.dataset.products === "all" ? Infinity : parseInt(root.dataset.products, 10);
    (window.PRODUCTS || []).slice(0, n).forEach((p) => root.append(card(p)));
  });
})();
