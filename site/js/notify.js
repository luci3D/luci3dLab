/* Wires up every <form data-notify> from window.NOTIFY (set in js/products.js).
   The form posts straight to the newsletter service, which sends the confirmation email. */
(function () {
  const cfg = window.NOTIFY || {};
  document.querySelectorAll("form[data-notify]").forEach((form) => {
    const input = form.querySelector('input[type="email"]');
    const button = form.querySelector("button");
    const status = document.querySelector("[data-notify-status]");
    if (!cfg.action) {
      input.disabled = true;
      button.disabled = true;
      button.setAttribute("aria-disabled", "true");
      if (status) status.textContent = "Sign-up opens soon.";
      return;
    }
    form.action = cfg.action;
    input.name = cfg.field || "email";
    for (const [k, v] of Object.entries(cfg.extra || {})) {
      const h = document.createElement("input");
      h.type = "hidden";
      h.name = k;
      h.value = v;
      form.append(h);
    }
    form.addEventListener("submit", () => {
      if (status) status.textContent = "Thanks! Check your inbox and confirm, so we know it's really you.";
    });
  });
})();
