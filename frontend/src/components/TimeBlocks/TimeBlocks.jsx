// src/components/TimeBlocks/TimeBlocks.jsx
import React from "react";
import "./TimeBlocks.css";
import "./../EshAssumptions/EshAssumptions.css"

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

import TimeBlockPanel from "./TimeBlockPanel/TimeBlockPanel.jsx";
import AddTimeBlockPanel from "./AddTimeBlockPanel/AddTimeBlockPanel.jsx";

function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  return `${path}^${JSON.stringify(value)}^${action}`;
}

const makeId = () =>
  (typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2));

function hydrate(rows) {
  const arr = Array.isArray(rows) ? rows : [];
  return arr.map((r) => (r.length === 4 ? r : [...r, makeId()]));
}

function firstRealDept(cfg) {
  const keys = Object.keys(cfg?.TIME_BLOCKS || {});
  const filtered = keys.filter((k) => k !== "Hannaford to Go ESH");
  return filtered[0] || keys[0] || "";
}

export default function TimeBlocks({ onClose }) {
  const [settings, setSettings] = React.useState(null);
  const [dept, setDept] = React.useState("");
  // rows are [start24, end24, label, id]
  const [blocks, _setBlocks] = React.useState([]);
  const [loading, setLoading] = React.useState(false);

  const getBlocksForDept = (cfg, name) => cfg?.TIME_BLOCKS?.[name] ?? [];
  const setBlocks = (next) => _setBlocks(hydrate(next));

  React.useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setSettings(cfg);
        const initial = firstRealDept(cfg);
        setDept(initial);
        setBlocks(getBlocksForDept(cfg, initial));
      } catch (e) {
        console.error("readSettings failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  React.useEffect(() => {
    if (!settings || !dept) return;
    setBlocks(getBlocksForDept(settings, dept));
  }, [settings, dept]);

  function updateRow(index, nextTriplet) {
    _setBlocks((prev) => prev.map((row, i) => (i === index ? [...nextTriplet, row[3]] : row)));
  }
  function removeRow(index) {
    _setBlocks((prev) => prev.filter((_, i) => i !== index));
  }
  function addRow(triplet) {
    _setBlocks((prev) => {
      const next = hydrate([...(prev || []), triplet]);
      next.sort((a, b) => (a?.[0] ?? "").localeCompare(b?.[0] ?? ""));
      return next;
    });
  }

  async function save() {
  try {
    // ensure the focused input commits its value
    if (document.activeElement) document.activeElement.blur();

    // let React flush the last onChange
    await new Promise(r => requestAnimationFrame(r));

    const toSave = (blocks || [])
      .map(b => b.slice(0, 3))
      .sort((a, b) => (a?.[0] ?? "").localeCompare(b?.[0] ?? ""));

    const update = buildUpdateString(["TIME_BLOCKS", dept], toSave, "update");
    console.log(update);
    setLoading(true);
    await window.electronAPI.applyConfig(update);
    
    const fresh = await window.electronAPI.readSettings();
    console.log(fresh);
    setSettings(fresh);
    setBlocks(getBlocksForDept(fresh, dept));
    setTimeout(() => {
       onClose?.();
       setLoading(false);
     }, 900);
  } catch (e) {
    console.error("applyConfig failed:", e);
  }
}

  if (!settings) return null;

  const depts = Object.keys(settings.TIME_BLOCKS || {}).filter(
    (d) => d !== "Hannaford to Go ESH"
  );

  return (
    <div className="tb-card">
      <TitleCardHeader title="Time Blocks" />
      <AccentStripe />

      <div className="tb-toolbar">
        <select
          className="tb-select"
          value={dept}
          onChange={(e) => setDept(e.target.value)}
          aria-label="Select department"
        >
          {depts.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>r.useS

      <div className="tb-rows">
        {blocks.map((b, i) => (
          <TimeBlockPanel
            key={b?.[3] ?? `row-${i}`}
            block={b}
            onChange={(next) => updateRow(i, next)}
            onRemove={() => removeRow(i)}
          />
        ))}
      </div>

      <div className="tb-add">
        <AddTimeBlockPanel onAdd={addRow} />
      </div>

      <div className="settings-footer">
        <StandardButton
        label = "Cancel"
        onClick = {onClose}
        />
        <div className="settings-spacer" />
        <StandardButton
        label = {loading ? "Saving..." : "Save & Close"}
        onClick = {save}
        disabled = {loading ? true : false}
        />
      </div>
    </div>
  );
}
