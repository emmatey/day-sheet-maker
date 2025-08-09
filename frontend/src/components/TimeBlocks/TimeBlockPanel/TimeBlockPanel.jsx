// 24h ↔ 12h helpers (kept local so the component is self-contained)
function to24(hour, minute, amPm) {
  const hNum = Number.parseInt(hour, 10);
  const mNum = Number.parseInt(minute, 10);
  const base = Number.isFinite(hNum) ? hNum : 0;
  const hh = (base % 12) + (amPm === "PM" ? 12 : 0);
  const mm = Number.isFinite(mNum) ? mNum : 0;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}
function from24(hhmm) {
  const [hhS, mmS] = (hhmm || "").split(":");
  const hh = Number(hhS ?? 0);
  const mm = Number(mmS ?? 0);
  const amPm = hh >= 12 ? "PM" : "AM";
  const h12 = ((hh + 11) % 12) + 1;
  return { h: String(h12).padStart(2, "0"), m: String(mm).padStart(2, "0"), amPm };
}

// tiny controlled inputs
function Num2({ value, onChange, ariaLabel }) {
  return (
    <input
      className="num2"
      inputMode="numeric"
      aria-label={ariaLabel}
      pattern="[0-9]*"
      value={value}
      onChange={(e) => {
        // allow empty string, otherwise keep up to 2 digits
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
 *  - block: [start24, end24, label]
 *  - onChange(nextBlock)
 *  - onRemove()
 */
export default function TimeBlockPanel({ block, onChange, onRemove }) {
  const [start24, end24, label] = block || ["00:00", "00:00", ""];

  // derive 12h fields from the 24h strings
  const s = from24(start24);
  const e = from24(end24);

  // update helpers send a NEW triplet up
  function updateLabel(v) {
    onChange?.([start24, end24, v]);
  }
  function updateStart(part, v) {
    const h = part === "h" ? v : s.h;
    const m = part === "m" ? v : s.m;
    const amPm = part === "amPm" ? v : s.amPm;
    onChange?.([to24(h, m, amPm), end24, label]);
  }
  function updateEnd(part, v) {
    const h = part === "h" ? v : e.h;
    const m = part === "m" ? v : e.m;
    const amPm = part === "amPm" ? v : e.amPm;
    onChange?.([start24, to24(h, m, amPm), label]);
  }

  return (
    <div className="tb-row">
      {/* Label (editable) */}
      <input
        className="tb-name"
        placeholder="Input Name..."
        value={label}
        onChange={(e) => updateLabel(e.target.value)}
        aria-label="Block name"
      />

      {/* Time inputs */}
      <div className="tb-time">
        <Num2 value={s.h} onChange={(v) => updateStart("h", v)} ariaLabel="Start hour" />
        <span>:</span>
        <Num2 value={s.m} onChange={(v) => updateStart("m", v)} ariaLabel="Start minute" />
        <SelectAMPM value={s.amPm} onChange={(v) => updateStart("amPm", v)} ariaLabel="Start AM/PM" />

        <span className="dash">—</span>

        <Num2 value={e.h} onChange={(v) => updateEnd("h", v)} ariaLabel="End hour" />
        <span>:</span>
        <Num2 value={e.m} onChange={(v) => updateEnd("m", v)} ariaLabel="End minute" />
        <SelectAMPM value={e.amPm} onChange={(v) => updateEnd("amPm", v)} ariaLabel="End AM/PM" />
      </div>

      {/* Remove */}
      <button
        className="tb-mini danger"
        onClick={() => onRemove?.()}
        aria-label="Remove block"
        type="button"
      >
        −
      </button>
    </div>
  );
}
