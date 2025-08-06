import { useState } from "react";
import "./SettingsLaunchpad.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";

import LeftButtonPanel from "./LeftButtonPanel/LeftButtonPanel.jsx";
import RightInputPanel from "./RightInputPanel/RightInputPanel.jsx";
import BottomButtonPanel from "./BottomButtonPanel/BottomButtonPanel.jsx";

export default function SettingsLaunchpad({ onClose }) {
  // === STATE ===
  const [saveLocation, setSaveLocation] = useState("/home/User/Documents/Schedule.xlsx");
  const [enableEsh, setEnableEsh] = useState(true);
  const [dailyNotesOverride, setDailyNotesOverride] = useState(false);

  // === HANDLERS ===
  const handlePickSaveLocation = async () => {
    const newPath = await window.electronAPI.selectDirectory();
    if (newPath) setSaveLocation(newPath);
    console.log(newPath);
  };

  const handleCheckboxChange = (checkboxName) => {
    if (checkboxName === "esh") {
      setEnableEsh((prev) => !prev);
    } else if (checkboxName === "dailyNotes") {
      setDailyNotesOverride((prev) => !prev);
    }
  };

  const handleResetConfig = async () => {
    const confirmed = await window.electronAPI.confirmResetConfig();
    if (!confirmed) return;

    await window.electronAPI.resetConfig();
    console.log("Config reset to default.");
    // Ideally, re-read settings.json and update state here
  };

  const handleSaveAndClose = async () => {
    const settingsToSave = {
      saveLocation,
      enableEsh,
      dailyNotesOverride
    };

    console.log("Saving settings:", settingsToSave);

    await window.electronAPI.saveSettings(settingsToSave);
    onClose();
  };

  return (
    <div className = "settings-launchpad-container">
      <TitleCardHeader title = "Settings" />
      <AccentStripe />

      <div className = "settings-body">
        <LeftButtonPanel 
         onSaveLocation = {handlePickSaveLocation}
         onRoleMap = {() => console.log("Good Job! You clicked a button!")}
         onTimeBlocks = {() => console.log("Good Job! You clicked a button!")}
         onESHAssumptions = {() => console.log("Good Job! You clicked a button!")}
        />
        <RightInputPanel
         enableEsh = {enableEsh}
         dailyNotesOverride = {dailyNotesOverride}
         onCheckboxChange = {handleCheckboxChange}
        />
      </div>

      <BottomButtonPanel
        onReset = {handleResetConfig}
        onSave = {handleSaveAndClose}
      />
    </div>
  );
}
