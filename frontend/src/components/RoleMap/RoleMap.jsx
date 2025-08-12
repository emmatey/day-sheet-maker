// src/components/RoleMap/RoleMap.jsx
import React from "react";
import "./RoleMap.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";
import StandardButton from "../StandardButton/StandardButton.jsx";

import RoleRow from "./RoleRow/RoleRow.jsx";
import AddRoleRow from "./AddRoleRow/AddRoleRow.jsx";

// helper to build backend update string
function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  return `${path}^${JSON.stringify(value)}^${action}`;
}

export default function RoleMap({ onClose }) {
  const [settings, setSettings] = React.useState(null);
  const [dept, setDept] = React.useState("");
  const [rows, setRows] = React.useState([]); // [{raw, display, enabled}, ...]
  const [showToast, setShowToast] = React.useState(false);
  

  // derive department list from ROLE_MAP (excluding "Blacklists")
  const deptList = React.useMemo(() => {
    if (!settings?.ROLE_MAP) return [];
    return Object.keys(settings.ROLE_MAP).filter((k) => k !== "Blacklists");
  }, [settings]);

  // zip settings arrays -> rows
  function toRows(roleMapDept) {
    const roles = roleMapDept?.roles || [];
    const clean = roleMapDept?.clean_roles || [];
    const en    = roleMapDept?.labor_tracker_enabled || [];
    const len   = Math.max(roles.length, clean.length, en.length);
    const out = [];
    for (let i = 0; i < len; i++) {
      out.push({
        raw: roles[i] ?? "",
        display: clean[i] ?? (roles[i] ?? ""),
        enabled: Boolean(en[i] ?? 1),
      });
    }
    return out;
  }

  // unzip rows -> parallel arrays
  function fromRows(rs) {
    return {
      roles: rs.map(r => r.raw),
      clean_roles: rs.map(r => r.display),
      labor_tracker_enabled: rs.map(r => (r.enabled ? 1 : 0)),
    };
  }

  // initial load
  React.useEffect(() => {
    let alive = true;
    (async () => {
      const cfg = await window.electronAPI.readSettings();
      if (!alive) return;
      setSettings(cfg);
      const first = Object.keys(cfg?.ROLE_MAP || {}).find(k => k !== "Blacklists") || "";
      setDept(first);
      setRows(toRows(cfg?.ROLE_MAP?.[first]));
    })();
    return () => { alive = false; };
  }, []);

  // when dept changes, swap rows
  React.useEffect(() => {
    if (!settings || !dept) return;
    setRows(toRows(settings.ROLE_MAP?.[dept]));
  }, [settings, dept]);

  // row ops
  function updateRow(index, next) {
    setRows(rows.map((r, i) => (i === index ? next : r)));
  }
  function removeRow(index) {
    setRows(rows.filter((_, i) => i !== index));
  }
  function addRow(raw, display) {
    setRows([...rows, { raw, display, enabled: true }]);
  }
  function moveUp(index) {
    if (index <= 0) return;
    const copy = rows.slice();
    [copy[index - 1], copy[index]] = [copy[index], copy[index - 1]];
    setRows(copy);
  }
  function moveDown(index) {
    if (index >= rows.length - 1) return;
    const copy = rows.slice();
    [copy[index + 1], copy[index]] = [copy[index], copy[index + 1]];
    setRows(copy);
  }

  // save
  const [saved, setSaved] = React.useState(false);
  async function save() {
    const payload = fromRows(rows);
    const update = buildUpdateString(["ROLE_MAP", dept], payload, "update");
    await window.electronAPI.applyConfig(update);

    setShowToast(true);
    const fresh = await window.electronAPI.readSettings();
    setSettings(fresh);
    setSaved(true);

    setTimeout(() =>{
      setShowToast(false);
      setSaved(false);
      onClose?.();
    }, 1000); 
  }

  if (!settings) return null;

  return (
    <div className="rm-card">
      <TitleCardHeader title="Role Map" />
      <AccentStripe />

      <div className="rm-toolbar">
        <select
          className="rm-select"
          value={dept}
          onChange={(e) => setDept(e.target.value)}
          aria-label="Select department"
        >
          {deptList.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      <div className="rm-rows">
        {rows.map((r, i) => (
          <RoleRow
            key={`${r.raw}-${i}`}
            data={r}
            onChange={(next) => updateRow(i, next)}
            onRemove={() => removeRow(i)}
            onUp={() => moveUp(i)}
            onDown={() => moveDown(i)}
          />
        ))}
      </div>

      <AddRoleRow onAdd={addRow} />

      <div className="rm-footer">
        <div className="rm-note">
          Order determines how roles appear in output. “Enabled” toggles the labor tracker.
        </div>
        <div className="rm-actions">
          {saved && <div className="rm-saved">Saved</div>}
          <StandardButton label="Save & Close" onClick={save} />
        </div>
      </div>
    </div>
  );
}
