// src/components/SettingsLaunchpad/LeftButtonPanel/LeftButtonPanel.jsx
import "./LeftButtonPanel.css";
import StandardPlusInfoButtonPanel from "../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel";

export default function LeftButtonPanel({ onSaveLocation, onRoleMap, onTimeBlocks, onEshAssumptions }) {
  return (
    <div className="left-button-panel">
      <StandardPlusInfoButtonPanel
        label="Save Location"
        onClickMain={onSaveLocation}
        onClickInfo={() => console.log("Save Location — info clicked")}
        showInfo = {true}
        buttonClassName="settings-launchpad-button"
        infoClassName="settings-launchpad-info"   
      />

      <StandardPlusInfoButtonPanel
        label="Role Map"
        onClickMain={onRoleMap}
        onClickInfo={() => console.log("Role Map — info clicked")}
        showInfo = {true}
        buttonClassName="settings-launchpad-button"
        infoClassName="settings-launchpad-info" 
      />

      <StandardPlusInfoButtonPanel
        label="Time Blocks"
        onClickMain={onTimeBlocks}
        onClickInfo={() => console.log("Time Blocks — info clicked")}
        showInfo = {true}
        buttonClassName="settings-launchpad-button"
        infoClassName="settings-launchpad-info" 
      />

       <StandardPlusInfoButtonPanel
        label="ESH Assumptions"
        onClickMain={onEshAssumptions}
        onClickInfo={() => console.log("ESH Assumptions — info clicked")}
        showInfo = {true}
        buttonClassName="settings-launchpad-button"
        infoClassName="settings-launchpad-info" 
      />
    </div>
  );
}
