// src/components/LaborTrackers/LaborTrackers.jsx
import React from "react";
import "./LaborTrackers.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";
import TimeBlocks from "../TimeBlocks/TimeBlocks.jsx";
import InfoButton from "../InfoButton/InfoButton.jsx"

function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

export default function LaborTrackers({ onClose, onEditTimeBlocks }) {
  const [combined, setCombined] = React.useState(false);  // OUTPUT_SETTINGS.combined_labor_tracker
  const [showTimeBlocks, setShowTimeBlocks] = React.useState(false);

  React.useEffect(() => {
    let alive = true;
    (async () => {
      const cfg = await window.electronAPI.readSettings();
      if (!alive) return;
      setCombined(!!cfg?.OUTPUT_SETTINGS?.combined_labor_tracker);
    })();
    return () => { alive = false; };
  }, []);

  const handleScopeChange = async (scope) => {
    const next = scope === "dept"; // dept => combined true
    setCombined(next);
    const u = buildUpdateString(["OUTPUT_SETTINGS", "combined_labor_tracker"], next, "update");
    try { await window.electronAPI.applyConfig(u); } catch (e) { console.error(e); }
  };

  return (
    <div className="labor-card">
      <TitleCardHeader title="Labor Trackers" />
      <AccentStripe />

      <fieldset className="scope-group">
        <legend>Labor tracker scope</legend>

        <label className="radio-row">
          <input
            type="radio"
            name="labor-scope"
            value="role"
            checked={!combined}
            onChange={() => handleScopeChange("role")}
          />
          Per role
        </label>

        <label className="radio-row">
          <input
            type="radio"
            name="labor-scope"
            value="dept"
            checked={combined}
            onChange={() => handleScopeChange("dept")}
          />
          Per department
        </label>
      </fieldset>
      
      <div className="std-button-container">
        <StandardButton 
        label = "Edit Time Blocks…" 
        onClick={onEditTimeBlocks}
        className="labor-trackers-std-button"
        />
      </div>
      <div className="labor-actions">
        <div className="info-button-lt">
          <InfoButton />
        </div>
        <div className="labor-spacer" />
        <StandardButton label="Close" onClick={onClose} />
      </div>

      {showTimeBlocks && (
        <div className="labor-inline-modal">
          <TimeBlocks onClose={() => setShowTimeBlocks(false)} />
        </div>
      )}
    </div>
  );
}
