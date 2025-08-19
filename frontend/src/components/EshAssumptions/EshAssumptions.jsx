// src/components/EshAssumptions/EshAssumptions.jsx
import React from "react";
import "./EshAssumptions.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

/** Build the CLI update string for the backend updater */
function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

// Ranges with index for storage, label for display
const RANGES = Array.from({ length: 15 }, (_, idx) => {
  const startH = 5 + idx;
  const endH   = startH + 1;
  const start  = String(startH).padStart(2, "0") + ":00";
  const end    = String(endH).padStart(2, "0") + ":00";
  return { idx, start, end, label: `${start} – ${end}` };
});

export default function ESHAssumptions({ onClose }) {
  const [settings, setSettings] = React.useState(null);
  // store by index as strings, e.g. { "0": "1", "1": "1", ... }
  const [values, setValues] = React.useState({});
  const [showToast, setShowToast] = React.useState(false);

  // Load settings once
  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setSettings(cfg);

        const src = cfg?.EXPEDITOR_REQUIREMENTS || {};
        const seeded = {};
        for (const { idx } of RANGES) {
          const n = Number(src[idx] ?? 0);
          seeded[idx] = Number.isFinite(n) ? String(n) : "0"; // controlled inputs
        }
        setValues(seeded);
      } catch (e) {
        console.error("readSettings (ESH) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  // Only allow non-negative integers; allow blank while typing
  function updateHour(idx, raw) {
    if (raw === "") {
      setValues((v) => ({ ...v, [idx]: "" }));
      return;
    }
    const cleaned = raw.replace(/\D/g, "");
    setValues((v) => ({ ...v, [idx]: cleaned }));
  }

  async function save() {
    const clean = {};
    for (const { idx } of RANGES) clean[idx] = Number(values[idx] || 0);

    try {
      const update = buildUpdateString(["EXPEDITOR_REQUIREMENTS"], clean, "update");
      await window.electronAPI.applyConfig(update);

      // brief success feedback, then close
      setShowToast(true);
      setTimeout(() => {
        setShowToast(false);
        onClose?.();
      }, 900);
    } catch (e) {
      console.error("applyConfig (ESH) failed:", e);
    }
  }

  if (!settings) return null;

  return (
    <div className="esh-card">
      <TitleCardHeader title = "ESH Assumptions" />

      <AccentStripe />

      {/* scrollable body */}
      <div className="esh-list">
        {RANGES.map(({ idx, label }) => (
          <div className="esh-row" key={idx}>
            <div className="esh-hour">{label}</div>
            <input
              className="esh-input"
              inputMode="numeric"
              aria-label={`ESH assumption for ${label}`}
              value={values[idx] ?? ""}
              onChange={(e) => updateHour(idx, e.target.value)}
            />
          </div>
        ))}
      </div>

      <div className="settings-footer">
        <StandardButton label="Cancel" onClick={onClose} />
        <div className="settings-spacer" />
        <StandardButton label="Save & Close" onClick={save} />
      </div>

      {showToast && <div className="esh-toast">Saved ✓</div>}
    </div>
  );
}
