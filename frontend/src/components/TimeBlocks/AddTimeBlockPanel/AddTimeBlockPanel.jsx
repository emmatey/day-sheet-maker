import React from "react";

// 12h ↔ 24h helpers
function to24(hour, minute, amPm) {
  const hNum = Number.parseInt(hour, 10);
  const mNum = Number.parseInt(minute, 10);
  const base = Number.isFinite(hNum) ? hNum : 0;
  const hh = (base % 12) + (amPm === "PM" ? 12 : 0);
  const mm = Number.isFinite(mNum) ? mNum : 0;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function Num2({ value, onChange, ariaLabel }) {
  return (
    <input
      className="num2"
      inputMode="numeric"
      pattern="[0-9]*"
      aria-label={ariaLabel}
      value={value}
      onChange={(e) => {
        const raw = e.target.value;
        const cleaned = raw === "" ? "" : raw.replace(/\D/g, "").slice(0, 2);
        onChange(cleaned);
      }}
    />
  );
}
function SelectAMPM({ value, onChange, ariaLabel }) {
  return (
    <select className="ampm" aria-label={ariaLabel} value={value} onChange={(e) => onChange(e.target.value)}>
      <option>AM</option>
      <option>PM</option>
    </select>
  );
}

/**
 * Props:
 *  - onAdd(triplet: [start24, end24, label])
 *  - defaultStart?: "HH:MM" (default "09:00")
 *  - defaultEnd?:   "HH:MM" (default "10:00")
 */
export default function AddTimeBlockPanel({ onAdd, defaultStart = "09:00", defaultEnd = "10:00" }) {
  const [label, setLabel] = React.useState("");

  // derive initial 12h from defaults
  const [sH, setSH] = React.useState("09");
  const [sM, setSM] = React.useState("00");
  const [sAmPm, setSAmPm] = React.useState("AM");

  const [eH, setEH] = React.useState("10");
  const [eM, setEM] = React.useState("00");
  const [eAmPm, setEAmPm] = React.useState("AM");

  React.useEffect(() => {
    const [h, m] = defaultStart.split(":");
    const HH = Number(h);
    const h12 = ((HH + 11) % 12) + 1;
    setSH(String(h12).padStart(2, "0"));
    setSM(m);
    setSAmPm(HH >= 12 ? "PM" : "AM");
  }, [defaultStart]);

  React.useEffect(() => {
    const [h, m] = defaultEnd.split(":");
    const HH = Number(h);
    const h12 = ((HH + 11) % 12) + 1;
    setEH(String(h12).padStart(2, "0"));
    setEM(m);
    setEAmPm(HH >= 12 ? "PM" : "AM");
  }, [defaultEnd]);

  function handleAdd() {
    const start24 = to24(sH, sM, sAmPm);
    const end24   = to24(eH, eM, eAmPm);
    if (!label.trim()) return;      // require a name
    if (end24 <= start24) return;   // naive guard; tweak if you allow wrap
    onAdd([start24, end24, label.trim()]);
    setLabel("");
  }

  function handleKey(e) {
    if (e.key === "Enter") handleAdd();
  }

  return (
    <>
      {/* Part 1: the textured divider */}
      <div className="tb-divider" role="separator" />

      {/* Part 2: the add row */}
      <div className="tb-row" onKeyDown={handleKey}>
        <input
          className="tb-name"
          placeholder="Input Name..."
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          aria-label="New block name"
        />

        <div className="tb-time">
          <Num2 value={sH} onChange={setSH} ariaLabel="Start hour" />
          <span>:</span>
          <Num2 value={sM} onChange={setSM} ariaLabel="Start minute" />
          <SelectAMPM value={sAmPm} onChange={setSAmPm} ariaLabel="Start AM/PM" />

          <span className="dash">—</span>

          <Num2 value={eH} onChange={setEH} ariaLabel="End hour" />
          <span>:</span>
          <Num2 value={eM} onChange={setEM} ariaLabel="End minute" />
          <SelectAMPM value={eAmPm} onChange={setEAmPm} ariaLabel="End AM/PM" />
        </div>

        <button
          className="tb-mini success"
          onClick={handleAdd}
          aria-label="Add block"
          type="button"
        >
          ＋
        </button>
      </div>
    </>
  );
}
