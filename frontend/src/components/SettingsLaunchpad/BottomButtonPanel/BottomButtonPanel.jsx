import "./BottomButtonPanel.css";
import StandardButton from "../../StandardButton/StandardButton.jsx";

export default function BottomButtonPanel({ onReset, onSave }) {
  return (
    <div className = "bottom-button-panel">
      {/* Left: Reset */}
      <div className = "left-side">
        <StandardButton
          label = "Reset to Default"
          onClick = {onReset}
          className = "blue-button"
        />
      </div>

      {/* Right: Save and Close */}
      <div className = "right-side">
        <StandardButton
          label = "Save and Close"
          onClick = {onSave}
        />
      </div>
    </div>
  );
}
