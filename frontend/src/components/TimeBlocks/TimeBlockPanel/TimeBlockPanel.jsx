// TimeBlockPanel.jsx — rewritten, cleaner, row-level commit on blur
import React, { useEffect, useMemo, useState, useCallback } from "react";

/**
 * Props
 * - block: [startHHMM, endHHMM, name]
 * - onChange: fn(updatedTriplet)
 * - onRemove: fn()
 */
export default function TimeBlockPanel({ block, onChange, onRemove }) {
  const [startHHMM, endHHMM, initialName] = block ?? ["00:00", "00:00", ""];

  // --- helpers ---
  const from24 = useCallback((hhmm) => {
    const [hhS, mmS] = String(hhmm || "00:00").split(":");
    let hh = Number(hhS);
    const mm = Number(mmS);
    const ampm = hh >= 12 ? "PM" : "AM";
    hh = hh % 12 || 12; // 0 → 12
    return { h: String(hh), m: String(mm).padStart(2, "0"), ampm };
  }, []);

  const to24 = useCallback((h, m, ampm) => {
    const H = Math.max(1, Math.min(12, parseInt(h || 0, 10) || 0));
    const M = Math.max(0, Math.min(59, parseInt(m || 0, 10) || 0));
    const base = H % 12;
    const hh = ampm === "PM" ? base + 12 : base;
    return `${String(hh).padStart(2, "0")}:${String(M).padStart(2, "0")}`;
  }, []);

  // --- local UI state ---
  const s0 = useMemo(() => from24(startHHMM), [startHHMM, from24]);
  const e0 = useMemo(() => from24(endHHMM), [endHHMM, from24]);

  const [name, setName] = useState(initialName || "");
  const [sH, setSH] = useState(s0.h);
  const [sM, setSM] = useState(s0.m);
  const [sAmPm, setSAmPm] = useState(s0.ampm);
  const [eH, setEH] = useState(e0.h);
  const [eM, setEM] = useState(e0.m);
  const [eAmPm, setEAmPm] = useState(e0.ampm);

  // keep local state in sync if parent swaps `block`
  useEffect(() => {
    setName(initialName || "");
    const s = from24(startHHMM);
    const e = from24(endHHMM);
    setSH(s.h); setSM(s.m); setSAmPm(s.ampm);
    setEH(e.h); setEM(e.m); setEAmPm(e.ampm);
  }, [startHHMM, endHHMM, initialName, from24]);

  const commit = useCallback(() => {
    const start = to24(sH, sM, sAmPm);
    const end = to24(eH, eM, eAmPm);
    onChange && onChange([start, end, name]);
  }, [sH, sM, sAmPm, eH, eM, eAmPm, name, to24, onChange]);

  const handleRowBlur = (e) => {
    // commit only when focus leaves the whole row
    if (!e.currentTarget.contains(e.relatedTarget)) commit();
  };

  const onEnterCommit = (e) => {
    if (e.key === "Enter") {
      e.currentTarget.blur();
      commit();
    }
  };

  return (
    <div className="tb-row" onBlur={handleRowBlur}>
      <input
        className="tb-name"
        type="text"
        placeholder="Label"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={onEnterCommit}
      />

      <div className="tb-time">
        <Num2 value={sH} onChange={setSH} aria-label="Start hour" />
        <span>:</span>
        <Num2 value={sM} onChange={setSM} aria-label="Start minute" />
        <SelectAMPM value={sAmPm} onChange={setSAmPm} />
        <span className="dash">—</span>
        <Num2 value={eH} onChange={setEH} aria-label="End hour" />
        <span>:</span>
        <Num2 value={eM} onChange={setEM} aria-label="End minute" />
        <SelectAMPM value={eAmPm} onChange={setEAmPm} />
      </div>

      <button className="tb-mini danger" onClick={() => onRemove && onRemove()} aria-label="Remove time block">
        −
      </button>
    </div>
  );
}

// --- Small, focused UI pieces ---
function clampDigits(v, max) {
  const n = parseInt(String(v).replace(/\D+/g, ""), 10);
  if (Number.isNaN(n)) return "";
  return String(Math.max(0, Math.min(max, n)));
}

function Num2({ value, onChange, "aria-label": ariaLabel }) {
  return (
    <input
      className="num2"
      inputMode="numeric"
      pattern="[0-9]*"
      value={value}
      aria-label={ariaLabel}
      onChange={(e) => onChange(clampDigits(e.target.value, 59))}
      onWheel={(e) => e.currentTarget.blur()} // prevent accidental scroll changes
      onKeyDown={(e) => {
        if (e.key === "ArrowUp") {
          e.preventDefault();
          const n = parseInt(value || 0, 10) || 0;
          onChange(String(Math.min(59, n + 1)).padStart(2, "0"));
        } else if (e.key === "ArrowDown") {
          e.preventDefault();
          const n = parseInt(value || 0, 10) || 0;
          onChange(String(Math.max(0, n - 1)).padStart(2, "0"));
        }
      }}
    />
  );
}

function SelectAMPM({ value, onChange }) {
  return (
    <select className="ampm" value={value} onChange={(e) => onChange(e.target.value)}>
      <option>AM</option>
      <option>PM</option>
    </select>
  );
}
