// src/components/EshAssumptions/EshAssumptions.jsx
import React from "react";
import "./EshAssumptions.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

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
  const [enableEsh, setEnableEsh] = React.useState(true);
  const [values, setValues] = React.useState({});

  // Load settings
  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setSettings(cfg);
        setEnableEsh(!!cfg?.OUTPUT_SETTINGS?.enable_esh);
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

  async function toggleEnableEsh() {
    const next = !enableEsh;
    setEnableEsh(next);
    const u = buildUpdateString(["OUTPUT_SETTINGS", "enable_esh"], next, "update");
    try { await window.electronAPI.applyConfig(u); } catch (e) { console.error(e); }
}

function updateHour(idx, raw) {
  if (raw === "") {
    setValues((v) => ({ ...v, [idx]: "" }));
    return;
  }
  let cleaned = raw.replace(/[^0-9.]/g, ""); 

  const parts = cleaned.split(".");
  if (parts.length > 2) {
    cleaned = parts[0] + "." + parts.slice(1).join(""); // collapse multiple dots
  }

  if (cleaned.includes(".")) {
    const [intPart, decPart] = cleaned.split(".");
    cleaned = intPart + "." + decPart.slice(0, 1);
  }

  setValues((v) => ({ ...v, [idx]: cleaned }));
}

  // save
  async function save() {
    const clean = {};
    for (const { idx } of RANGES) clean[idx] = Number(values[idx] || 0);

    try {
      const update = buildUpdateString(["EXPEDITOR_REQUIREMENTS"], clean, "update");
      await window.electronAPI.applyConfig(update);
      setTimeout(() => {
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
        <label className = "esh-toggle">
          <input type = "checkbox" checked = {enableEsh} onChange = {toggleEnableEsh}/>
          Enable ESH
        </label>
        <div className="settings-spacer" />
        <StandardButton label="Save & Close" onClick={save} />
      </div>
      {showToast && <div className="esh-toast">Saved ✓</div>}
    </div>
  );
}
