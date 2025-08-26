// src/components/RoleMap/RoleRow/RoleRow.jsx
import "./../RoleMap.css";

export default function RoleRow({ data, onChange, onRemove, onUp, onDown }) {
  const { raw, display, enabled } = data;

  function updateDisplay(v) {
    onChange?.({ raw, display: v, enabled });
  }
  function updateEnabled(v) {
    onChange?.({ raw, display, enabled: v });
  }

  return (
    <div className="rm-row">
      <input
        className="rm-raw"
        value={raw}
        readOnly
        aria-label="Raw role"
        title="Raw role (from schedule)"
      />
      <input
        className="rm-display"
        value={display}
        onChange={(e) => updateDisplay(e.target.value)}
        aria-label="Display role"
        placeholder="Display role…"
        title = "Display role…"
      />
      <label className="rm-enabled">
        <input
          type="checkbox"
          title = "Show or hide this role's 'labor tracker' in the daysheets."
          checked={enabled}
          onChange={(e) => updateEnabled(e.target.checked)}
        />
        Enabled
      </label>

      <div className="rm-movers">
        <button className="rm-mini" onClick={onUp} aria-label="Move up">▲</button>
        <button className="rm-mini" onClick={onDown} aria-label="Move down">▼</button>
      </div>

      <button className="rm-mini danger" onClick={onRemove} aria-label="Remove role">−</button>
    </div>
  );
}
