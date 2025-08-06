// src/components/SettingsLaunchpad/RightInputPanel/RightInputPanel.jsx
import "./RightInputPanel.css";

export default function RightInputPanel({
  enableEsh,
  dailyNotesOverride,
  onCheckboxChange
}) {
  return (
    <div className = "right-input-panel">
      {/* Checkboxes */}
      <div className = "checkbox-group">
        <label>
          <input
            type = "checkbox"
            checked = {enableEsh}
            onChange = {() => onCheckboxChange("esh")}
          />
          Enable ESH
        </label>

        <label>
          <input
            type = "checkbox"
            checked = {dailyNotesOverride}
            onChange = {() => onCheckboxChange("dailyNotes")}
          />
          Daily Notes Override
        </label>
      </div>
    </div>
  );
}
