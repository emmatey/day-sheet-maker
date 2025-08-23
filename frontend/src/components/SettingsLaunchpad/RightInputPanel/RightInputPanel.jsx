// src/components/SettingsLaunchpad/RightInputPanel/RightInputPanel.jsx
import "./RightInputPanel.css";

export default function RightInputPanel({
   dailyNotesOverride,
   onCheckboxChange
}) 

{
  return (
    <div className="right-input-panel">
      <div className="checkbox-group">
        <label>
          <input
            type="checkbox"
            title="Disable labor trackers/ESH tables, insert blank space for notes instead."
            checked={dailyNotesOverride}
            onChange={() => onCheckboxChange("dailyNotes")}
          />
           "Daily Notes" Override
        </label>
       </div>
      </div>
  );
}
