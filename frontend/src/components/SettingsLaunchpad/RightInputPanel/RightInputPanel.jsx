// src/components/SettingsLaunchpad/RightInputPanel/RightInputPanel.jsx
import "./RightInputPanel.css";

export default function RightInputPanel({
  enableEsh,
  dailyNotesOverride,
  combineLaborTrackers,
  onCheckboxChange,
  onLaborScopeChange,          // ("role" | "dept")
}) {
  const handleScopeChange = (e) => {
    const value = e.target.value;        // "role" | "dept"
    onLaborScopeChange?.(value);
  };

  return (
    <div className="right-input-panel">
      {/* Checkboxes */}
      <div className="checkbox-group">
        <label>
          <input
            type="checkbox"
            checked={enableEsh}
            onChange={() => onCheckboxChange("esh")}
          />
          Enable ESH
        </label>

        <label>
          <input
            type="checkbox"
            checked={dailyNotesOverride}
            onChange={() => onCheckboxChange("dailyNotes")}
          />
          Daily Notes Override
        </label>
      </div>

      {/* Labor tracker scope */}
      <fieldset className="scope-group">
        <legend>Labor tracker scope</legend>

        <label className="radio-row">
          <input
            type="radio"
            name="labor-scope"
            value="role"
            checked={!combineLaborTrackers}      // false => per role
            onChange={handleScopeChange}
          />
          Per role
        </label>

        <label className="radio-row">
          <input
            type="radio"
            name="labor-scope"
            value="dept"
            checked={combineLaborTrackers}       // true => per department
            onChange={handleScopeChange}
          />
          Per department
        </label>
      </fieldset>
    </div>
  );
}
