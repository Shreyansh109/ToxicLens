"""Animated particle exclamation mark for the ToxicLens hero.

Pure HTML, CSS and JavaScript drawn on a canvas. It makes no network requests and
has no effect on model output. It pauses when it is off screen or the tab is hidden,
shows one still frame when the system asks for reduced motion, and lowers its own
detail if the computer cannot keep up.
"""
import streamlit as st

_ALT = "Decorative three-dimensional exclamation mark made of glowing particles"

_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<style>
html, body { margin: 0; height: 100%; background: transparent; overflow: hidden; }
#wrap { position: relative; width: 100%; height: 100%; }
canvas { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.cap { position: absolute; left: 6%; bottom: 3%; color: #8b8b99;
  font: 600 11px/1 "Segoe UI", system-ui, -apple-system, Arial, sans-serif;
  letter-spacing: .12em; text-transform: uppercase; }
</style></head>
<body>
<div id="wrap">
<canvas id="c" role="img" aria-label="Decorative three-dimensional exclamation mark made of glowing particles"></canvas>
<div class="cap">Signals &middot; not verdicts</div>
</div>
<script>
__JS__
</script>
</body></html>"""


def render_exclamation_hero(height: int = 560) -> None:
    """Draws the particle exclamation mark. Call it inside a Streamlit column."""
    html = _HTML.replace("__JS__", _JS)
    if hasattr(st, "iframe"):
        try:
            st.iframe(html, height=height, alt=_ALT)
        except TypeError:  # older Streamlit versions have no alt parameter
            st.iframe(html, height=height)
    else:  # Streamlit versions before st.iframe existed
        import streamlit.components.v1 as components
        components.html(html, height=height, scrolling=False)


_JS = """(function () {
  "use strict";

  var canvas = document.getElementById("c");
  var wrap = document.getElementById("wrap");
  var ctx = canvas.getContext("2d");
  var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  // ---------- fixed-seed random numbers, so the shape is identical on every load
  function mulberry32(seed) {
    return function () {
      seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  var rnd = mulberry32(20261028);
  function gauss() {
    var u = 1 - rnd(), v = rnd();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(6.283185307 * v);
  }

  // ---------- shape of the exclamation mark (model units, height about 1.93)
  var Z_SCALE = 0.66;                    // depth of the stem compared with its width
  var Y_BOTTOM = -0.34, Y_TOP = 1.0;     // stem
  var R_TOP = 0.33, R_BOTTOM = 0.14;     // stem radius at the top and at the bottom
  var DOT_R = 0.235, DOT_Y = -0.70;      // dot
  var Y_CENTER = 0.035;                  // vertical centre of the whole figure

  function stemRadius(v) {               // v: 0 at the bottom of the stem, 1 at the top
    var r = R_BOTTOM + (R_TOP - R_BOTTOM) * Math.pow(v, 0.85);
    var capTop = 0.10, capBottom = 0.07, t;
    if (v > 1 - capTop) { t = (v - (1 - capTop)) / capTop; r *= Math.sqrt(Math.max(0, 1 - t * t)); }
    if (v < capBottom) { t = (capBottom - v) / capBottom; r *= Math.sqrt(Math.max(0, 1 - t * t)); }
    return r;
  }
  function stemWeight(v) {               // surface area weight, so points are evenly spread
    var e = 0.002;
    var slope = (stemRadius(Math.min(1, v + e)) - stemRadius(Math.max(0, v - e))) / (2 * e * (Y_TOP - Y_BOTTOM));
    return stemRadius(v) * Math.sqrt(1 + slope * slope);
  }
  var maxWeight = 0, vi;
  for (vi = 0; vi <= 1000; vi++) { maxWeight = Math.max(maxWeight, stemWeight(vi / 1000)); }

  // ---------- colour along the height: amber, warm white, lilac, violet, blue, teal
  var STOPS = [
    [1.00, 255, 184, 41], [0.80, 255, 210, 122], [0.55, 251, 238, 221], [0.30, 241, 227, 255],
    [0.05, 207, 162, 255], [-0.20, 154, 104, 255], [-0.38, 122, 77, 255], [-0.60, 70, 167, 255],
    [-0.78, 40, 192, 216], [-0.93, 25, 211, 160]
  ];
  function colorAt(y) {
    var i;
    if (y >= STOPS[0][0]) { return [STOPS[0][1], STOPS[0][2], STOPS[0][3]]; }
    for (i = 0; i < STOPS.length - 1; i++) {
      var a = STOPS[i], b = STOPS[i + 1];
      if (y <= a[0] && y >= b[0]) {
        var f = (a[0] - y) / (a[0] - b[0]);
        return [a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, a[3] + (b[3] - a[3]) * f];
      }
    }
    var l = STOPS[STOPS.length - 1];
    return [l[1], l[2], l[3]];
  }
  var BANDS = 32, BAND_MIN = -0.95, BAND_MAX = 1.02;
  function bandOf(y) {
    var b = Math.floor((y - BAND_MIN) / (BAND_MAX - BAND_MIN) * BANDS);
    return Math.max(0, Math.min(BANDS - 1, b));
  }
  var BAND_CSS = [];
  (function () {
    for (var b = 0; b < BANDS; b++) {
      var y = BAND_MIN + (b + 0.5) / BANDS * (BAND_MAX - BAND_MIN);
      var c = colorAt(y);
      BAND_CSS.push("rgb(" + Math.round(c[0]) + "," + Math.round(c[1]) + "," + Math.round(c[2]) + ")");
    }
  })();

  // ---------- build the point clouds
  function makeStemPoint(inner) {
    var v, r, w;
    for (;;) {
      v = rnd(); r = stemRadius(v); w = stemWeight(v);
      if (rnd() * maxWeight <= w) { break; }
    }
    var phi = rnd() * 6.283185307, cp = Math.cos(phi), sp = Math.sin(phi);
    var y = Y_BOTTOM + v * (Y_TOP - Y_BOTTOM);
    var k = inner ? Math.sqrt(rnd()) * 0.92 : 1 + (rnd() - 0.5) * 0.07;
    var nx = cp * Z_SCALE, nz = sp, ny = 0, l;
    if (v > 0.9) { ny = (v - 0.9) / 0.1 * 0.9; }
    if (v < 0.07) { ny = -(0.07 - v) / 0.07 * 0.9; }
    l = Math.sqrt(nx * nx + nz * nz); nx /= l; nz /= l;
    var s = Math.sqrt(Math.max(0, 1 - ny * ny)); nx *= s; nz *= s;
    return { x: r * cp * k, y: y, z: r * Z_SCALE * sp * k, nx: nx, ny: ny, nz: nz, inner: inner };
  }
  function makeDotPoint(inner) {
    var gx = gauss(), gy = gauss(), gz = gauss(), l = Math.sqrt(gx * gx + gy * gy + gz * gz) || 1;
    gx /= l; gy /= l; gz /= l;
    var k = inner ? Math.pow(rnd(), 0.33) * 0.9 : 1 + (rnd() - 0.5) * 0.07;
    return { x: gx * DOT_R * k, y: DOT_Y + gy * DOT_R * k, z: gz * DOT_R * 0.8 * k, nx: gx, ny: gy, nz: gz, inner: inner };
  }

  function buildLayer(list, triangles) {
    var i, n = list.length, p;
    for (i = 0; i < n; i++) { list[i].band = bandOf(list[i].y); }
    list.sort(function (a, b) { return a.band - b.band; });
    var L = {
      n: n,
      X: new Float32Array(n), Y: new Float32Array(n), Z: new Float32Array(n),
      NX: new Float32Array(n), NY: new Float32Array(n), NZ: new Float32Array(n),
      PH: new Float32Array(n), GN: new Float32Array(n),
      SX: new Float32Array(n), SY: new Float32Array(n), SS: new Float32Array(n), LV: new Uint8Array(n),
      start: new Int32Array(BANDS + 1)
    };
    if (triangles) {
      L.TA = new Float32Array(n); L.TS = new Float32Array(n); L.TR = new Float32Array(n);
      L.SC = new Float32Array(n); L.SN = new Float32Array(n);
    }
    for (i = 0; i < n; i++) {
      p = list[i];
      L.X[i] = p.x; L.Y[i] = p.y; L.Z[i] = p.z;
      L.NX[i] = p.nx; L.NY[i] = p.ny; L.NZ[i] = p.nz;
      L.PH[i] = rnd() * 6.283185307;
      L.GN[i] = p.inner ? 0.72 : 1;
      if (triangles) {
        L.TA[i] = rnd() * 6.283185307;
        L.TS[i] = 1.5 + Math.pow(rnd(), 2) * 3.6;
        L.TR[i] = (rnd() - 0.5) * 0.9;
      }
    }
    var b = 0;
    for (i = 0; i <= BANDS; i++) { L.start[i] = n; }
    for (i = n - 1; i >= 0; i--) { L.start[list[i].band] = i; }
    for (b = BANDS - 1; b >= 0; b--) { if (L.start[b] > L.start[b + 1]) { L.start[b] = L.start[b + 1]; } }
    return L;
  }

  var dotList = [], triList = [], q;
  for (q = 0; q < 11000; q++) { dotList.push(makeStemPoint(false)); }
  for (q = 0; q < 2600; q++) { dotList.push(makeStemPoint(true)); }
  for (q = 0; q < 2800; q++) { dotList.push(makeDotPoint(false)); }
  for (q = 0; q < 500; q++) { dotList.push(makeDotPoint(true)); }
  for (q = 0; q < 650; q++) { triList.push(makeStemPoint(false)); }
  for (q = 0; q < 170; q++) { triList.push(makeDotPoint(false)); }
  var DOTS = buildLayer(dotList, false);
  var TRIS = buildLayer(triList, true);

  // ---------- floating wireframe fragments around the figure
  var PALETTE = ["#ffb829", "#8052ff", "#46a7ff", "#19d3a0", "#ff7dcb", "#f4f0ff", "#d04dff"];
  var DEBRIS = [];
  (function () {
    for (var i = 0; i < 22; i++) {
      var big = i < 3;
      DEBRIS.push({
        size: big ? 20 + rnd() * 14 : 4 + rnd() * 9,
        r: 0.42 + rnd() * 0.62, a0: rnd() * 6.283185307, sp: (0.05 + rnd() * 0.10) * (rnd() < 0.5 ? -1 : 1),
        y: -0.9 + rnd() * 1.85, bs: 0.4 + rnd() * 0.6, bp: rnd() * 6.283185307,
        rx: (rnd() - 0.5) * 1.1, ry: (rnd() - 0.5) * 1.1, p: rnd() * 6.283185307, q: rnd() * 6.283185307,
        color: PALETTE[i % PALETTE.length], al: big ? 0.9 : 0.35 + rnd() * 0.45
      });
    }
  })();
  var TET = [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]];
  var EDGES = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]];

  // ---------- view and drawing state
  var W = 0, H = 0, S = 0, F = 1, CX = 0, CY = 0, CAMD = 3.4;
  var T = 0, yawSm = 0, pitchSm = 0, targetYaw = 0, targetPitch = 0, stride = 1;
  var cT = 1, sT = 0, cP = 1, sP = 0, sweepY = -9;
  var px = 0, py = 0, pf = 1, pa = 0;
  var glowA = null, glowB = null, glowC = null;
  var LEVEL_ALPHA = [0.34, 0.62, 0.95];
  var TRI_ALPHA = [0.32, 0.58, 0.85];

  function resize() {
    var r = wrap.getBoundingClientRect();
    W = Math.max(200, Math.floor(r.width));
    H = Math.max(200, Math.floor(r.height));
    canvas.width = Math.floor(W * DPR);
    canvas.height = Math.floor(H * DPR);
    S = Math.min(W, H);
    F = S * 0.43; CX = W / 2; CY = H / 2 + S * 0.01;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    glowA = ctx.createRadialGradient(CX, CY, 0, CX, CY, S * 0.58);
    glowA.addColorStop(0, "rgba(128,82,255,0.20)"); glowA.addColorStop(1, "rgba(128,82,255,0)");
    glowB = ctx.createRadialGradient(CX - S * 0.04, CY - S * 0.30, 0, CX - S * 0.04, CY - S * 0.30, S * 0.32);
    glowB.addColorStop(0, "rgba(255,184,41,0.13)"); glowB.addColorStop(1, "rgba(255,184,41,0)");
    glowC = ctx.createRadialGradient(CX, CY + S * 0.36, 0, CX, CY + S * 0.36, S * 0.20);
    glowC.addColorStop(0, "rgba(25,211,160,0.12)"); glowC.addColorStop(1, "rgba(25,211,160,0)");
    if (reduceMotion) { render(); }
  }

  function setView() {
    var yaw = 0.58 * Math.sin(T * 0.33) + 0.10 * Math.sin(T * 0.81 + 1.3) + yawSm;
    var pitch = 0.09 * Math.sin(T * 0.27 + 1.0) + pitchSm - 0.04;
    cT = Math.cos(yaw); sT = Math.sin(yaw); cP = Math.cos(pitch); sP = Math.sin(pitch);
    var ph = (T % 8) / 6;                         // a band of light travels down the figure every 8 seconds
    sweepY = ph < 1 ? 1.2 - ph * 2.4 : -9;
  }

  function prj(L, i) {
    var wob = 1 + 0.012 * Math.sin(T * 0.9 + L.PH[i]);
    var x0 = L.X[i] * wob, y0 = L.Y[i], z0 = L.Z[i] * wob;
    var x1 = x0 * cT + z0 * sT;
    var z1 = z0 * cT - x0 * sT;
    var y2 = y0 * cP - z1 * sP;
    var z2 = y0 * sP + z1 * cP;
    var k = CAMD / (CAMD - z2);
    px = CX + x1 * F * k;
    py = CY - (y2 - Y_CENTER) * F * k;
    pf = k;
    var nx = L.NX[i], ny = L.NY[i], nz = L.NZ[i];
    var nz1 = nz * cT - nx * sT;
    var nx1 = nx * cT + nz * sT;
    var ny2 = ny * cP - nz1 * sP;
    var nz2 = ny * sP + nz1 * cP;
    var rim = 1 - Math.abs(nz2);
    var lit = 0.5 + 0.5 * (-0.55 * nx1 + 0.6 * ny2 + 0.35 * nz2);
    var a = 0.27 + 0.50 * rim * rim + 0.24 * lit + (nz2 > 0 ? 0.12 : -0.03);
    var sw = 1 - Math.abs(y0 - sweepY) * 6.5;
    if (sw > 0) { a += 0.38 * sw; }
    a *= L.GN[i] * (0.80 + 0.20 * (z2 + 0.5));
    pa = a;
  }

  function drawDots(L) {
    var size = Math.max(0.85, S * 0.0024), b, i, s, e, lv, sz;
    for (b = 0; b < BANDS; b++) {
      s = L.start[b]; e = L.start[b + 1];
      if (s === e) { continue; }
      for (i = s; i < e; i += stride) {
        prj(L, i);
        L.SX[i] = px; L.SY[i] = py; L.SS[i] = size * (0.8 + 0.4 * pf * pf) * (stride > 1 ? 1.25 : 1);
        L.LV[i] = pa < 0.36 ? 0 : (pa < 0.66 ? 1 : 2);
      }
      ctx.fillStyle = BAND_CSS[b];
      for (lv = 0; lv < 3; lv++) {
        ctx.globalAlpha = LEVEL_ALPHA[lv];
        ctx.beginPath();
        for (i = s; i < e; i += stride) {
          if (L.LV[i] !== lv) { continue; }
          sz = L.SS[i];
          ctx.rect(L.SX[i] - sz * 0.5, L.SY[i] - sz * 0.5, sz, sz);
        }
        ctx.fill();
      }
    }
  }

  function drawTris(L) {
    var scale = S / 520, b, i, s, e, lv, r, c, sn, x, y;
    ctx.lineWidth = Math.max(0.55, S * 0.0013);
    ctx.lineJoin = "round";
    for (b = 0; b < BANDS; b++) {
      s = L.start[b]; e = L.start[b + 1];
      if (s === e) { continue; }
      for (i = s; i < e; i += stride) {
        prj(L, i);
        var ang = L.TA[i] + T * L.TR[i];
        L.SX[i] = px; L.SY[i] = py; L.SS[i] = L.TS[i] * scale * pf;
        L.SC[i] = Math.cos(ang); L.SN[i] = Math.sin(ang);
        L.LV[i] = pa < 0.36 ? 0 : (pa < 0.66 ? 1 : 2);
      }
      ctx.strokeStyle = BAND_CSS[b];
      for (lv = 0; lv < 3; lv++) {
        ctx.globalAlpha = TRI_ALPHA[lv];
        ctx.beginPath();
        for (i = s; i < e; i += stride) {
          if (L.LV[i] !== lv) { continue; }
          x = L.SX[i]; y = L.SY[i]; r = L.SS[i]; c = L.SC[i]; sn = L.SN[i];
          ctx.moveTo(x + r * sn, y - r * c);
          ctx.lineTo(x + r * (-0.866 * c - 0.5 * sn), y + r * (-0.866 * sn + 0.5 * c));
          ctx.lineTo(x + r * (0.866 * c - 0.5 * sn), y + r * (0.866 * sn + 0.5 * c));
          ctx.closePath();
        }
        ctx.stroke();
      }
    }
  }

  function drawDebris(front) {
    var scale = S / 520, j, e, v;
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#fff";
    for (j = 0; j < DEBRIS.length; j++) {
      var d = DEBRIS[j];
      var a = d.a0 + T * d.sp;
      var x0 = Math.cos(a) * d.r, z0 = Math.sin(a) * d.r * 0.8;
      var y0 = d.y + 0.05 * Math.sin(T * d.bs + d.bp);
      var x1 = x0 * cT + z0 * sT, z1 = z0 * cT - x0 * sT;
      var y2 = y0 * cP - z1 * sP, z2 = y0 * sP + z1 * cP;
      if ((z2 >= 0) !== front) { continue; }
      var k = CAMD / (CAMD - z2);
      var cx = CX + x1 * F * k, cy = CY - (y2 - Y_CENTER) * F * k;
      var size = d.size * scale * k / 1.732;
      var ax = d.p + T * d.rx, ay = d.q + T * d.ry;
      var cax = Math.cos(ax), sax = Math.sin(ax), cay = Math.cos(ay), say = Math.sin(ay);
      var sx = [], sy = [];
      for (v = 0; v < 4; v++) {
        var vx = TET[v][0], vy = TET[v][1], vz = TET[v][2];
        var yy = vy * cax - vz * sax, zz = vy * sax + vz * cax;
        var xx = vx * cay + zz * say;
        sx.push(cx + xx * size); sy.push(cy - yy * size);
      }
      ctx.strokeStyle = d.color;
      var alpha = d.al * (front ? 1 : 0.6);
      var lw = 0.7 + size * 0.03;
      var pass;
      for (pass = 0; pass < 2; pass++) {
        ctx.globalAlpha = pass === 0 ? alpha * 0.16 : alpha;
        ctx.lineWidth = pass === 0 ? lw * 3.2 : lw;
        ctx.beginPath();
        for (e = 0; e < 6; e++) {
          ctx.moveTo(sx[EDGES[e][0]], sy[EDGES[e][0]]);
          ctx.lineTo(sx[EDGES[e][1]], sy[EDGES[e][1]]);
        }
        ctx.stroke();
      }
    }
  }

  function render() {
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.globalCompositeOperation = "source-over";
    ctx.globalAlpha = 1;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = glowA; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = glowB; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = glowC; ctx.fillRect(0, 0, W, H);
    setView();
    drawDebris(false);
    ctx.globalCompositeOperation = "lighter";
    drawDots(DOTS);
    drawTris(TRIS);
    ctx.globalCompositeOperation = "source-over";
    drawDebris(true);
    ctx.globalAlpha = 1;
  }

  // ---------- animation loop
  var raf = 0, last = 0, visible = true, slowFrames = 0;

  function frame(now) {
    raf = 0;
    if (!visible || document.hidden || reduceMotion) { return; }
    var dt = last ? (now - last) / 1000 : 0.016;
    last = now;
    if (dt > 0.030) { slowFrames++; } else if (slowFrames > 0) { slowFrames--; }
    if (slowFrames > 40 && stride < 3) { stride++; slowFrames = 0; }
    dt = Math.min(dt, 0.05);
    T += dt;
    var k = 1 - Math.exp(-dt * 3.5);
    yawSm += (targetYaw - yawSm) * k;
    pitchSm += (targetPitch - pitchSm) * k;
    render();
    raf = requestAnimationFrame(frame);
  }
  function start() {
    if (!raf && !reduceMotion && visible && !document.hidden) { last = 0; raf = requestAnimationFrame(frame); }
  }

  window.addEventListener("pointermove", function (e) {
    var r = canvas.getBoundingClientRect();
    targetYaw = ((e.clientX - r.left) / r.width - 0.5) * 0.9;
    targetPitch = ((e.clientY - r.top) / r.height - 0.5) * 0.45;
  });
  document.addEventListener("pointerleave", function () { targetYaw = 0; targetPitch = 0; });
  document.addEventListener("visibilitychange", start);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; start(); }).observe(wrap);
  }
  if ("ResizeObserver" in window) { new ResizeObserver(resize).observe(wrap); } else { window.addEventListener("resize", resize); }

  resize();
  window.__toxiclensHero = { renderAt: function (t) { T = t; render(); } };
  if (reduceMotion) { T = 1.4; render(); } else { start(); }
})();
"""
