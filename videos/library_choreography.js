// =============================================================================
// Mount Angel Abbey Library — Deterministic 30.00 fps Studio Choreography Driver
// Interpolates camera splines, solar ephemeris (doy, hour), heliodon, and
// stencil-poche section sweeps over `window.__mountAngelStudio`.
// =============================================================================

(function () {
  function hideAllMenus() {
    document.body.classList.add("studio-mode", "menus-hidden");
    const ids = ["hudCaption", "sidePanel", "restoreUiBtn"];
    for (const id of ids) {
      const el = document.getElementById(id);
      if (el) el.style.display = "none";
    }
    const hdr = document.querySelector(".suite-header");
    if (hdr) hdr.style.display = "none";
  }

  // Unwrap yaw sequence so cubic interpolation never spins 360 deg the wrong way
  function prepareKeyframes(rawKfs) {
    if (!Array.isArray(rawKfs) || rawKfs.length === 0) return [];
    const kfs = rawKfs.map((k) => ({ ...k })).sort((a, b) => a.t - b.t);
    for (let i = 1; i < kfs.length; i++) {
      if (kfs[i].yaw !== undefined && kfs[i - 1].yaw !== undefined) {
        let dy = kfs[i].yaw - kfs[i - 1].yaw;
        while (dy > Math.PI) {
          kfs[i].yaw -= Math.PI * 2.0;
          dy -= Math.PI * 2.0;
        }
        while (dy < -Math.PI) {
          kfs[i].yaw += Math.PI * 2.0;
          dy += Math.PI * 2.0;
        }
      }
    }
    return kfs;
  }

  // Fritsch-Carlson Monotonic Cubic Hermite (PCHIP) 1D interpolator (zero overshoot)
  function evalPchip(ts, ys, t) {
    const n = ts.length;
    if (n === 0) return 0.0;
    if (n === 1 || t <= ts[0]) return ys[0];
    if (t >= ts[n - 1]) return ys[n - 1];

    const h = new Array(n - 1);
    const delta = new Array(n - 1);
    for (let i = 0; i < n - 1; i++) {
      h[i] = Math.max(1e-6, ts[i + 1] - ts[i]);
      delta[i] = (ys[i + 1] - ys[i]) / h[i];
    }

    const m = new Array(n).fill(0.0);
    if (n === 2) {
      m[0] = delta[0];
      m[1] = delta[0];
    } else {
      for (let i = 1; i < n - 1; i++) {
        if (delta[i - 1] * delta[i] > 0.0) {
          const w1 = 2.0 * h[i] + h[i - 1];
          const w2 = h[i] + 2.0 * h[i - 1];
          m[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i]);
        } else {
          m[i] = 0.0;
        }
      }
      // Endpoint slopes (shape-preserving)
      let m0 = ((2.0 * h[0] + h[1]) * delta[0] - h[0] * delta[1]) / (h[0] + h[1]);
      if (m0 * delta[0] <= 0.0) m0 = 0.0;
      else if (delta[0] * delta[1] < 0.0 && Math.abs(m0) > Math.abs(3.0 * delta[0])) m0 = 3.0 * delta[0];
      m[0] = m0;

      let mn = ((2.0 * h[n - 2] + h[n - 3]) * delta[n - 2] - h[n - 2] * delta[n - 3]) / (h[n - 2] + h[n - 3]);
      if (mn * delta[n - 2] <= 0.0) mn = 0.0;
      else if (delta[n - 2] * delta[n - 3] < 0.0 && Math.abs(mn) > Math.abs(3.0 * delta[n - 2])) mn = 3.0 * delta[n - 2];
      m[n - 1] = mn;
    }

    let seg = 0;
    for (let i = 0; i < n - 1; i++) {
      if (t >= ts[i] && t <= ts[i + 1]) {
        seg = i;
        break;
      }
    }
    const dt = h[seg];
    const s = (t - ts[seg]) / dt;
    const s2 = s * s;
    const s3 = s2 * s;
    const h00 = 2.0 * s3 - 3.0 * s2 + 1.0;
    const h10 = s3 - 2.0 * s2 + s;
    const h01 = -2.0 * s3 + 3.0 * s2;
    const h11 = s3 - s2;
    return h00 * ys[seg] + h10 * dt * m[seg] + h01 * ys[seg + 1] + h11 * dt * m[seg + 1];
  }

  function sampleNumericProp(kfs, prop, fallbackVal, t) {
    const sub = kfs.filter((k) => typeof k[prop] === "number");
    if (sub.length === 0) return fallbackVal;
    return evalPchip(
      sub.map((k) => k.t),
      sub.map((k) => k[prop]),
      t
    );
  }

  function sampleSteppedProp(kfs, prop, fallbackVal, t) {
    let val = fallbackVal;
    for (const k of kfs) {
      if (k.t <= t + 1e-5 && k[prop] !== undefined) {
        val = k[prop];
      }
    }
    return val;
  }

  let _preparedKfs = [];

  window.__studioSetup = async (width, height, duration, fps) => {
    hideAllMenus();

    // Poll until 39 MB library_3d_scene.json finishes uploading all 8 GPU layers
    const deadline = Date.now() + 45000;
    while (
      !(window.__mountAngelStudio && window.__mountAngelStudio.isLoaded()) &&
      Date.now() < deadline
    ) {
      await new Promise((r) => setTimeout(r, 120));
    }
    const st = window.__mountAngelStudio;
    if (!st || !st.isLoaded()) {
      throw new Error("Timed out waiting for Mount Angel 3D scene GPU upload.");
    }

    window.__studioGlCanvas = st.canvas;
    window.__studioGlContext = st.gl;

    const cfg = window.__STUDIO_CAMERA_PATH_CONFIG || window.CAMERA_PATH_CONFIG || {};
    if (cfg.preset && st.PRESETS[cfg.preset]) {
      st.applyPreset(cfg.preset);
    }
    _preparedKfs = prepareKeyframes(cfg.keyframes || []);
    hideAllMenus();
    st.renderAtSize(width, height);
  };

  window.__studioStep = async (frameIdx, tSec, duration, width, height) => {
    const st = window.__mountAngelStudio;
    if (!st) return;
    hideAllMenus();

    const cfg = window.__STUDIO_CAMERA_PATH_CONFIG || window.CAMERA_PATH_CONFIG || {};
    const kfs = _preparedKfs;

    if (kfs.length > 0) {
      st.cam.target[0] = sampleNumericProp(kfs, "tx", st.cam.target[0], tSec);
      st.cam.target[1] = sampleNumericProp(kfs, "ty", st.cam.target[1], tSec);
      st.cam.target[2] = sampleNumericProp(kfs, "tz", st.cam.target[2], tSec);
      st.cam.yaw = sampleNumericProp(kfs, "yaw", st.cam.yaw, tSec);
      st.cam.pitch = sampleNumericProp(kfs, "pitch", st.cam.pitch, tSec);
      st.cam.dist = sampleNumericProp(kfs, "dist", st.cam.dist, tSec);
      st.cam.fov = sampleNumericProp(kfs, "fov", st.cam.fov, tSec);
      st.cam.shiftX = sampleNumericProp(kfs, "shiftX", 0.0, tSec);
      st.cam.shiftY = sampleNumericProp(kfs, "shiftY", 0.0, tSec);
      st.cam.ortho = Boolean(sampleSteppedProp(kfs, "ortho", Boolean(cfg.ortho), tSec));

      // Continuous solar ephemeris animation
      st.sun.doy = sampleNumericProp(kfs, "doy", st.sun.doy, tSec);
      st.sun.hour = sampleNumericProp(kfs, "hour", st.sun.hour, tSec);
      st.sun.shadows = sampleSteppedProp(kfs, "shadows", true, tSec);
      st.sun.caster = sampleSteppedProp(kfs, "caster", cfg.caster || "envelope", tSec);
      st.sun.heliodon = Boolean(sampleSteppedProp(kfs, "heliodon", Boolean(cfg.heliodon), tSec));

      // Continuous or stepped section plane animation
      const secMode = sampleSteppedProp(kfs, "secMode", cfg.secMode || "off", tSec);
      st.sec.mode = secMode;
      if (secMode !== "off") {
        st.sec.d = sampleNumericProp(kfs, "secD", st.sec.d, tSec);
        st.sec.flip = sampleSteppedProp(kfs, "secFlip", cfg.secFlip ?? 1, tSec);
        st.sec.radialDeg = sampleNumericProp(kfs, "secRadialDeg", st.sec.radialDeg, tSec);
        st.sec.poche = sampleSteppedProp(kfs, "secPoche", true, tSec);
        st.sec.pocheTone = sampleSteppedProp(kfs, "pocheTone", cfg.pocheTone || "terracotta", tSec);
      }

      // Layer visibility overrides
      const defaultHide = cfg.hideLayers || ["0_Regulating_Grid"];
      const activeHide = sampleSteppedProp(kfs, "hideLayers", defaultHide, tSec);
      for (const name of Object.keys(st.layerVisible)) {
        st.layerVisible[name] = !activeHide.includes(name);
      }
    }

    st.renderAtSize(width, height);
  };
})();
