// src/components/SettingsLaunchpad/SettingsLaunchpad.jsx
import { useState, useEffect} from "react";
import "./SettingsLaunchpad.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";

import LeftButtonPanel from "./LeftButtonPanel/LeftButtonPanel.jsx";
import RightInputPanel from "./RightInputPanel/RightInputPanel.jsx";
import BottomButtonPanel from "./BottomButtonPanel/BottomButtonPanel.jsx";

import TimeBlocks from "../TimeBlocks/TimeBlocks.jsx";
import ESHAssumptions from "../EshAssumptions/EshAssumptions.jsx";
import RoleMap from "../RoleMap/RoleMap.jsx";
import SaveLocation from "../SaveLocation/SaveLocation.jsx";
import Modal from "../Modal/Modal.jsx";

function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

export default function SettingsLaunchpad({ onClose }) {
  // === STATE ===
  const [activeModal, setActiveModal] = useState(null);
  const [enableEsh, setEnableEsh] = useState(true);
  const [dailyNotesOverride, setDailyNotesOverride] = useState(false);
  
  // 1) Read current values on mount
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setEnableEsh(!!cfg?.OUTPUT_SETTINGS?.enable_esh);
        setDailyNotesOverride(!!cfg?.OUTPUT_SETTINGS?.daily_notes_override);
      } catch (e) {
        console.error("readSettings (SettingsLaunchpad) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  // 2) When a toggle changes, immediately persist
  const handleCheckboxChange = async (which) => {
    try {
      if (which === "esh") {
        const next = !enableEsh;
        setEnableEsh(next);
        const u = buildUpdateString(["OUTPUT_SETTINGS", "enable_esh"], next, "update");
        await window.electronAPI.applyConfig(u);
      } else if (which === "dailyNotes") {
        const next = !dailyNotesOverride;
        setDailyNotesOverride(next);
        const u = buildUpdateString(["OUTPUT_SETTINGS", "daily_notes_override"], next, "update");
        await window.electronAPI.applyConfig(u);
      }
    } catch (e) {
      console.error("applyConfig (Settings toggles) failed:", e);
    }
  };

  const handleResetConfig = async () => {
    const confirmed = await window.electronAPI.confirmResetConfig();
    if (!confirmed) return;
    await window.electronAPI.resetConfig();
    console.log("Config reset to default.");
    // If you want, re-read settings.json here and update local state.
  };

  const handleClose = () => {
    onClose?.();
  };

  return (
    <div className="settings-launchpad-container">
      <TitleCardHeader title = "Settings" />
      <AccentStripe />

      <div className="settings-body">
        <LeftButtonPanel
          onSaveLocation={() => setActiveModal("saveloc")}
          onRoleMap={() => setActiveModal("rolemap")}
          onTimeBlocks={() => setActiveModal("timeblocks")}
          onEshAssumptions={() => setActiveModal("esh")}
        />
        <RightInputPanel
          enableEsh={enableEsh}
          dailyNotesOverride={dailyNotesOverride}
          onCheckboxChange={handleCheckboxChange}
        />
      </div>

      <BottomButtonPanel
        onReset={handleResetConfig}
        onSave={handleClose}
        saveLabel="Close"
      />

      {activeModal === "timeblocks" && (
        <Modal onClose={() => setActiveModal(null)}>
          <TimeBlocks onClose={() => setActiveModal(null)} />
        </Modal>
      )}
      
      {activeModal === "esh" && (
        <Modal onClose={() => setActiveModal(null)}>
          <ESHAssumptions onClose={() => setActiveModal(null)} />
        </Modal>
      )}

      {activeModal === "rolemap" && (
        <Modal onClose={() => setActiveModal(null)}>
          <RoleMap onClose={() => setActiveModal(null)} />
        </Modal>
      )}

      {activeModal === "saveloc" && (
        <Modal onClose={() => setActiveModal(null)}>
          <SaveLocation onClose={() => setActiveModal(null)} />
        </Modal>
      )}
    </div>
  );
}
