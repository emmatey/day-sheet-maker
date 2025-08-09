// src/components/TimeBlocks/TimeBlocks.jsx
import React from "react";
import "./TimeBlocks.css";

// atoms
import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

// children
import TimeBlockPanel from "./TimeBlockPanel/TimeBlockPanel.jsx";
import AddTimeBlockPanel from "./AddTimeBlockPanel/AddTimeBlockPanel.jsx";

/** Build the CLI update string for the backend */
function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

export default function TimeBlocks({ onClose }) {
  const [settings, setSettings] = React.useState(null);
  const [dept, setDept] = React.useState("");
  const [blocks, _setBlocks] = React.useState([]); // [["05:00","10:00","Label"], ...]

  function getBlocksForDept(cfg, deptName) {
    return cfg?.TIME_BLOCKS?.[deptName] ?? [];
  }

  // keep rows sorted by start time
  function setBlocks(next) {
    const copy = (Array.isArray(next) ? next : []).slice();
    copy.sort((a, b) => (a?.[0] ?? "").localeCompare(b?.[0] ?? ""));
    _setBlocks(copy);
  }

  // initial load
  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setSettings(cfg);
        const first = Object.keys(cfg?.TIME_BLOCKS || {})[0] || "";
        setDept(first);
        setBlocks(getBlocksForDept(cfg, first));
      } catch (e) {
        console.error("readSettings failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  // swap slice on department change
  React.useEffect(() => {
    if (!settings || !dept) return;
    setBlocks(getBlocksForDept(settings, dept));
  }, [settings, dept]);

  function updateRow(index, next) {
    setBlocks(blocks.map((row, i) => (i === index ? next : row)));
  }
  function removeRow(index) {
    setBlocks(blocks.filter((_, i) => i !== index));
  }
  function addRow(triplet) {
    setBlocks([...(blocks || []), triplet]);
  }

  async function save() {
    try {
      const update = buildUpdateString(["TIME_BLOCKS", dept], blocks, "update");
      await window.electronAPI.applyConfig(update);
      const fresh = await window.electronAPI.readSettings();
      setSettings(fresh);
      setBlocks(getBlocksForDept(fresh, dept));
      onClose?.();
    } catch (e) {
      console.error("applyConfig failed:", e);
    }
  }

  if (!settings) return null;
  const depts = Object.keys(settings.TIME_BLOCKS || {});

  return (
    <div className="tb-card">
      {/* header + stripe are flush now */}
      <TitleCardHeader title="Time Blocks" />
      <AccentStripe />

      <div className="tb-toolbar">
          <select
            className="tb-select"
            value={dept}
            onChange={(e) => setDept(e.target.value)}
            aria-label="Select department"
          >
            {depts
              .filter((d) => d !== "Hannaford to Go ESH") // blacklist
              .map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
          </select>
        </div>

      <div className="tb-rows">
        {blocks.map((b, i) => (
          <TimeBlockPanel
            key={`row-${i}`}
            block={b}                     // [start24, end24, label]
            onChange={(next) => updateRow(i, next)}
            onRemove={() => removeRow(i)}
          />
        ))}
      </div>
            
      {/* add panel (wrap it so padding matches .tb-rows) */}
      <div className="tb-rows add">
        <AddTimeBlockPanel onAdd={addRow} />
      </div>
            

      <div className="tb-footer">
        <div className = "tb-footer-text">
        <span>Click away from the "Time Blocks" window to close without saving,<br />
          "Save & Close" button updates settings.</span>
        </div>
        <StandardButton label="Save & Close" onClick={save} />
      </div>
    </div> 
  );
}
