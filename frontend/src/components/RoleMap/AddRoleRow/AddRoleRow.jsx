// src/components/RoleMap/AddRoleRow/AddRoleRow.jsx
import React from "react";
import "./../RoleMap.css";

export default function AddRoleRow({ onAdd }) {
  const [raw, setRaw] = React.useState("");
  const [display, setDisplay] = React.useState("");

  function handleAdd() {
    const r = raw.trim();
    const d = (display.trim() || r);
    if (!r) return;
    onAdd?.(r, d);
    setRaw("");
    setDisplay("");
  }

  function onKey(e) {
    if (e.key === "Enter") handleAdd();
  }

  return (
    <>
      <div className="rm-divider" role="separator" />
      <div className="rm-row add" onKeyDown={onKey}>
        <input
          className="rm-raw"
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder="New raw role…"
          aria-label="New raw role"
        />
        <input
          className="rm-display"
          value={display}
          onChange={(e) => setDisplay(e.target.value)}
          placeholder="New display role…"
          aria-label="New display role"
        />
        <div className="rm-movers" aria-hidden="true" />
        <button className="rm-mini success" type="button" onClick={handleAdd}>＋</button>
      </div>
    </>
  );
}
