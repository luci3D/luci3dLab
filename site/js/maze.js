/* Zine maze: route a trace from the filled arrow (in) to the hollow arrow (out).
   The mazes are the original hand-drawn zine pages; their lines become copper.
   Needs to be served over http (GitHub Pages, or `python3 -m http.server` locally):
   browsers block reading image pixels from file:// pages. */
(function () {
  const MAZES = {
    1: { src: "img/maze-01.png", start: [26, 283], exit: [670, 396] },
    2: { src: "img/maze-02.png", start: [18, 895], exit: [650, 16] },
    3: { src: "img/maze-03.png", start: [26, 435], exit: [692, 431] },
    4: { src: "img/maze-04.png", start: [14, 30], exit: [655, 905] },
    5: { src: "img/maze-05.png", start: [321, 21], exit: [668, 442] },
  };
  const C = {
    bg: [20, 20, 25], wall: [224, 168, 74], wallLo: [101, 67, 37],
    trail: "#8ce0c4", trailDeep: "#2b7780", head: "#f2f1ee", tongue: "#e83a3a", exit: "#ec488c",
  };
  const R = 4;           // player half-size in maze pixels
  const SPEED = 2.2;     // maze pixels per frame

  const canvas = document.getElementById("maze");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const hud = { time: document.getElementById("t"), len: document.getElementById("len"), win: document.getElementById("win") };
  let base, wall, W, H, px, py, trail, t0, done, dir = [1, 0], current = 1;
  const held = new Set();

  function free(x, y) {
    const x0 = Math.round(x - R), x1 = Math.round(x + R), y0 = Math.round(y - R), y1 = Math.round(y + R);
    if (x0 < 0 || y0 < 0 || x1 >= W || y1 >= H) return false;
    for (let yy = y0; yy <= y1; yy++) for (let xx = x0; xx <= x1; xx++) if (wall[yy * W + xx]) return false;
    return true;
  }

  function nearestFree(x, y) {
    for (let r = 0; r < 20; r++)
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (free(x + dx, y + dy)) return [x + dx, y + dy];
    return [x, y];
  }

  function load(n) {
    current = n;
    const m = MAZES[n];
    const img = new Image();
    img.onload = () => {
      W = img.width; H = img.height;
      canvas.width = W; canvas.height = H;
      const off = document.createElement("canvas");
      off.width = W; off.height = H;
      const o = off.getContext("2d");
      o.drawImage(img, 0, 0);
      const src = o.getImageData(0, 0, W, H).data;
      wall = new Uint8Array(W * H);
      for (let i = 0; i < W * H; i++) {
        const a = src[i * 4 + 3], s = src[i * 4] + src[i * 4 + 1] + src[i * 4 + 2];
        wall[i] = a > 128 && s < 384 ? 1 : 0;
      }
      const out = o.createImageData(W, H);
      for (let i = 0; i < W * H; i++) {
        const below = i + W < W * H && wall[i + W];
        const c = wall[i] ? C.wall : (i >= W && wall[i - W] && !below) ? C.wallLo : C.bg;  // a copper lip under each line
        out.data.set([c[0], c[1], c[2], 255], i * 4);
      }
      o.putImageData(out, 0, 0);
      base = off;
      reset();
    };
    img.src = m.src;
    document.querySelectorAll(".maze-pick button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.maze == n));
  }

  function reset() {
    [px, py] = nearestFree(...MAZES[current].start);
    trail = [[px, py]];
    t0 = null; done = false;
    hud.win.textContent = "";
    draw();
  }

  function step() {
    if (!base) return requestAnimationFrame(step);
    if (!done && held.size) {
      const k = [...held].pop();
      const d = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[k];
      dir = d;
      if (t0 === null) t0 = performance.now();
      for (let s = 0; s < SPEED; s += 0.5) {
        if (free(px + d[0] * 0.5, py + d[1] * 0.5)) { px += d[0] * 0.5; py += d[1] * 0.5; }
        else if (d[0] && free(px + d[0] * 0.5, py - 1)) py -= 1;      // slide round corners a little
        else if (d[0] && free(px + d[0] * 0.5, py + 1)) py += 1;
        else if (d[1] && free(px - 1, py + d[1] * 0.5)) px -= 1;
        else if (d[1] && free(px + 1, py + d[1] * 0.5)) px += 1;
      }
      const last = trail[trail.length - 1];
      if (Math.hypot(px - last[0], py - last[1]) >= 3) trail.push([px, py]);
      const [ex, ey] = MAZES[current].exit;
      if (Math.hypot(px - ex, py - ey) < 16) {
        done = true;
        hud.win.textContent = "Routed! luci3D approves.";
      }
    }
    if (t0 !== null && !done) hud.time.textContent = ((performance.now() - t0) / 1000).toFixed(1) + " s";
    let len = 0;
    for (let i = 1; i < trail.length; i++) len += Math.hypot(trail[i][0] - trail[i - 1][0], trail[i][1] - trail[i - 1][1]);
    hud.len.textContent = Math.round(len) + " px";
    draw();
    requestAnimationFrame(step);
  }

  function draw() {
    ctx.drawImage(base, 0, 0);
    const [ex, ey] = MAZES[current].exit;
    const pulse = 6 + 3 * Math.sin(performance.now() / 200);
    ctx.fillStyle = C.exit;
    ctx.fillRect(Math.round(ex - pulse / 2), Math.round(ey - pulse / 2), Math.round(pulse), Math.round(pulse));
    ctx.lineJoin = "round"; ctx.lineCap = "round";
    for (const [w, c] of [[7, C.trailDeep], [4, C.trail]]) {
      ctx.strokeStyle = c; ctx.lineWidth = w;
      ctx.beginPath();
      trail.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.lineTo(px, py);
      ctx.stroke();
    }
    ctx.fillStyle = C.head;
    ctx.fillRect(Math.round(px - R), Math.round(py - R), R * 2 + 1, R * 2 + 1);
    ctx.fillStyle = C.tongue;
    ctx.fillRect(Math.round(px + dir[0] * (R + 2) - 1), Math.round(py + dir[1] * (R + 2) - 1), 2, 2);
  }

  const KEYS = { ArrowUp: "up", KeyW: "up", ArrowDown: "down", KeyS: "down", ArrowLeft: "left", KeyA: "left", ArrowRight: "right", KeyD: "right" };
  window.addEventListener("keydown", (e) => {
    const k = KEYS[e.code];
    if (!k || document.activeElement !== canvas) return;
    e.preventDefault();
    held.delete(k); held.add(k);
  });
  window.addEventListener("keyup", (e) => { const k = KEYS[e.code]; if (k) held.delete(k); });
  canvas.addEventListener("pointerdown", () => canvas.focus());
  document.querySelectorAll(".dpad button").forEach((b) => {
    const k = b.dataset.dir;
    b.addEventListener("pointerdown", (e) => { e.preventDefault(); held.add(k); });
    for (const ev of ["pointerup", "pointerleave", "pointercancel"]) b.addEventListener(ev, () => held.delete(k));
  });
  document.querySelectorAll(".maze-pick button").forEach((b) => b.addEventListener("click", () => { load(+b.dataset.maze); canvas.focus(); }));
  document.getElementById("reset").addEventListener("click", () => { reset(); canvas.focus(); });

  load(1);
  requestAnimationFrame(step);
})();
