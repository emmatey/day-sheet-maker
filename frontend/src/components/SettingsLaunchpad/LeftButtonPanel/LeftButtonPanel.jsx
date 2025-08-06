// src/components/SettingsLaunchpad/LeftButtonPanel/LeftButtonPanel.jsx
import "./LeftButtonPanel.css";
import StandardButton from "../../StandardButton/StandardButton.jsx";

export default function LeftButtonPanel({ onSaveLocation, onRoleMap, onTimeBlocks, onESHAssumptions }) {
  return (
    <div className = "left-button-panel">
      <StandardButton 
        label = "Save Location" 
        onClick = {onSaveLocation} 
      />
      <StandardButton 
        label = "Role Map" 
        onClick = {onRoleMap} 
      />
      <StandardButton 
        label = "Time Blocks" 
        onClick = {onTimeBlocks} 
      />
      <StandardButton 
        label = "ESH Assumptions" 
        onClick = {onESHAssumptions} 
      />
    </div>
  );
}
