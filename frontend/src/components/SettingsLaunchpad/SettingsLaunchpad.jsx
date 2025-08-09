// src/components/SettingsLaunchpad/SettingsLaunchpad.jsx
import { useState } from "react";
import "./SettingsLaunchpad.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";

import LeftButtonPanel from "./LeftButtonPanel/LeftButtonPanel.jsx";
import RightInputPanel from "./RightInputPanel/RightInputPanel.jsx";
import BottomButtonPanel from "./BottomButtonPanel/BottomButtonPanel.jsx";

import TimeBlocks from "../TimeBlocks/TimeBlocks.jsx";
import Modal from "../Modal/Modal.jsx";

export default function SettingsLaunchpad({ onClose }) {
  // === STATE ===
  const [saveLocation, setSaveLocation] = useState("/home/User/Documents/Schedule.xlsx");
  const [enableEsh, setEnableEsh] = useState(true);
  const [dailyNotesOverride, setDailyNotesOverride] = useState(false);
  const [showTimeBlocks, setShowTimeBlocks] = useState(false);

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
    // If you want, re-read settings.json here and update local state.
  };

  // New: bottom-right button just closes this modal
  const handleClose = () => {
    onClose?.();
  };

  return (
    <div className="settings-launchpad-container">
      <TitleCardHeader title="Settings" />
      <AccentStripe />

      <div className="settings-body">
        <LeftButtonPanel
          onSaveLocation={handlePickSaveLocation}
          onRoleMap={() => console.log("Role Map clicked")}
          onTimeBlocks={() => setShowTimeBlocks(true)}
          onEshAssumptions={() => console.log("Esh Assumptions clicked")}
        />
        <RightInputPanel
          enableEsh={enableEsh}
          dailyNotesOverride={dailyNotesOverride}
          onCheckboxChange={handleCheckboxChange}
        />
      </div>

      {/* If BottomButtonPanel supports custom labels, pass saveLabel="Close".
         If not, tweak BottomButtonPanel to use the prop (fallback to default). */}
      <BottomButtonPanel
        onReset={handleResetConfig}
        onSave={handleClose}
        saveLabel="Close"
      />

      {showTimeBlocks && (
        <Modal onClose={() => setShowTimeBlocks(false)}>
          <TimeBlocks onClose={() => setShowTimeBlocks(false)} />
        </Modal>
      )}
    </div>
  );
}
