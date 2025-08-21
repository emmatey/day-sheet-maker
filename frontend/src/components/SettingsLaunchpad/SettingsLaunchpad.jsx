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
  const [combineLaborTrackers, setCombineLaborTrackers] = useState(false); // NEW

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setEnableEsh(!!cfg?.OUTPUT_SETTINGS?.enable_esh);
        setDailyNotesOverride(!!cfg?.OUTPUT_SETTINGS?.daily_notes_override);
        setCombineLaborTrackers(!!cfg?.OUTPUT_SETTINGS?.combined_labor_tracker); 
      } catch (e) {
        console.error("readSettings (SettingsLaunchpad) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

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

  const handleLaborScopeChange = async (scope) => {
    const combined = scope === "dept";
    setCombineLaborTrackers(combined);
    try {
      const u = buildUpdateString(["OUTPUT_SETTINGS", "combined_labor_tracker"], combined, "update");
      await window.electronAPI.applyConfig(u);
    } catch (e) {
      console.error("applyConfig (combined_labor_tracker) failed:", e);
    }
  };

  const handleResetConfig = async () => {
    const confirmed = await window.electronAPI.confirmResetConfig();
    if (!confirmed) return;
    await window.electronAPI.resetConfig();
    console.log("Config reset to default.");
  };

  const handleClose = () => { onClose?.(); };

  return (
    <div className="settings-launchpad-container">
      <TitleCardHeader title="Settings" />
      <AccentStripe />

      <div className="settings-body">
        <RightInputPanel
          enableEsh={enableEsh}
          dailyNotesOverride={dailyNotesOverride}
          combineLaborTrackers={combineLaborTrackers}          
          onCheckboxChange={handleCheckboxChange}
          onLaborScopeChange={handleLaborScopeChange}           
        />
        <LeftButtonPanel
          onSaveLocation={() => setActiveModal("saveloc")}
          onRoleMap={() => setActiveModal("rolemap")}
          onTimeBlocks={() => setActiveModal("timeblocks")}
          onEshAssumptions={() => setActiveModal("esh")}
        />
      </div>

      <BottomButtonPanel
        onReset={handleResetConfig}
        onSave={handleClose}
        saveLabel="Close"
      />

      {activeModal === "timeblocks" && (
        <Modal onClose={() => setActiveModal(null)} allowClickAway={false}>
          <TimeBlocks onClose={() => setActiveModal(null)} />
        </Modal>
      )}

      {activeModal === "esh" && (
        <Modal onClose={() => setActiveModal(null)} allowClickAway={false}>
          <ESHAssumptions onClose={() => setActiveModal(null)} />
        </Modal>
      )}

      {activeModal === "rolemap" && (
        <Modal onClose={() => setActiveModal(null)} allowClickAway={false}>
          <RoleMap onClose={() => setActiveModal(null)} />
        </Modal>
      )}

      {activeModal === "saveloc" && (
        <Modal onClose={() => setActiveModal(null)} allowClickAway={true}>
          <SaveLocation onClose={() => setActiveModal(null)} />
        </Modal>
      )}
    </div>
  );
}