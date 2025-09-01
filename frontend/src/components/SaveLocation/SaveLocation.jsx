// src/components/SaveLocation/SaveLocation.jsx
import React from "react";
import "./SaveLocation.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

export default function SaveLocation({ onClose }) {
  const [settings, setSettings] = React.useState(null);
  const [path, setPath] = React.useState("");
  const [copyToArchive, setCopyToArchive] = React.useState(false);
  const [saving, setSaving] = React.useState(false);

  // load current path
  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setSettings(cfg);
        setPath(cfg?.SAVE_LOCATION?.save_location_string ?? "");
        setCopyToArchive(!!cfg?.OUTPUT_SETTINGS?.copy_input_to_archive)
      } catch (e) {
        console.error("readSettings (SaveLocation) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  async function pickDir() {
    try {
      const newPath = await window.electronAPI.selectDirectory();
      if (newPath) setPath(newPath);
    } catch (e) {
      console.error("selectDirectory failed:", e);
    }
  }

  async function save() {
    try {
      setSaving(true);
      const u1 = buildUpdateString(["SAVE_LOCATION", "save_location_string"], path, "update");
      await window.electronAPI.applyConfig(u1);

      const u2 = buildUpdateString(["OUTPUT_SETTINGS", "copy_input_to_archive"], copyToArchive, "update");
      await window.electronAPI.applyConfig(u2);

      const fresh = await window.electronAPI.readSettings();
      setSettings(fresh);
      onClose?.();
      
    } catch (e) {
      console.error("applyConfig (SaveLocation) failed:", e);

    } finally {
      setSaving(false);
    }
  }

  if (!settings) return null;

  return (
    <div className="sl-card">
      <TitleCardHeader title="Save Location" />
      <AccentStripe />

      <div className="sl-body">
        <div className="sl-title">Choose Save Location</div>
        <button type="button" className="sl-pill" onClick={pickDir} aria-label="Pick save location">
          <span className="sl-icon" aria-hidden>📁</span>
          <span className="sl-path" title={path || "(not set)"}>{path || "Not set"}</span>
        </button>
        <label className="sl-row">
          <input
            type="checkbox"
            checked={copyToArchive}
            onChange={(e) => setCopyToArchive(e.target.checked)}
          />
          <span>Save a copy of the input in the archive folder</span>
        </label>
      </div>

      <div className="sl-footer">
        <StandardButton
          label={saving ? "Saving..." : "Save & Close"}
          disabled={saving || !path}
          onClick={save}
        />
      </div>
    </div>
  );
}
