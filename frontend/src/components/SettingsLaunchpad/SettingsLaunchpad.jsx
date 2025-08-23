// src/components/SettingsLaunchpad/SettingsLaunchpad.jsx
import { useState, useEffect } from "react";
import "./SettingsLaunchpad.css";

import TitleCardHeader from "../DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "../HomeScreen/AccentStripe/AccentStripe.jsx";

import LeftButtonPanel from "./LeftButtonPanel/LeftButtonPanel.jsx";
import RightInputPanel from "./RightInputPanel/RightInputPanel.jsx";
import BottomButtonPanel from "./BottomButtonPanel/BottomButtonPanel.jsx";

import ESHAssumptions from "../EshAssumptions/EshAssumptions.jsx";
import RoleMap from "../RoleMap/RoleMap.jsx";
import SaveLocation from "../SaveLocation/SaveLocation.jsx";
import LaborTrackers from "../LaborTrackers/LaborTrackers.jsx";
import Modal from "../Modal/Modal.jsx";
import TimeBlocks from "../TimeBlocks/TimeBlocks.jsx";

function buildUpdateString(segments, value, action = "update") {
  const path = "[" + segments.map(String).join("][") + "]";
  const payload = JSON.stringify(value);
  return `${path}^${payload}^${action}`;
}

export default function SettingsLaunchpad({ onClose }) {
  const [activeModal, setActiveModal] = useState(null);
  const [dailyNotesOverride, setDailyNotesOverride] = useState(false);
  const navigate = (name) => setActiveModal(name);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        setDailyNotesOverride(!!cfg?.OUTPUT_SETTINGS?.daily_notes_override);
      } catch (e) {
        console.error("readSettings (SettingsLaunchpad) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  const handleCheckboxChange = async (which) => {
    if (which !== "dailyNotes") return;
    try {
      const next = !dailyNotesOverride;
      setDailyNotesOverride(next);
      const u = buildUpdateString(["OUTPUT_SETTINGS", "daily_notes_override"], next, "update");
      await window.electronAPI.applyConfig(u);
    } catch (e) {
      console.error("applyConfig (Settings toggles) failed:", e);
    }
  };

  const handleResetConfig = async () => {
    const confirmed = await window.electronAPI.confirmResetConfig();
    if (!confirmed) return;
    await window.electronAPI.resetConfig();
    console.log("Config reset to default.");
  };

  return (
    <div className="settings-launchpad-container">
      <TitleCardHeader title="Settings" />
      <AccentStripe />

      <div className="settings-body">
        <LeftButtonPanel
          onSaveLocation={() => navigate("saveloc")}
          onRoleMap={() => navigate("rolemap")}
          onTimeBlocks={() => navigate("labor")} 
          onEshAssumptions={() => navigate("esh")}
        />
        <RightInputPanel
          dailyNotesOverride={dailyNotesOverride}
          onCheckboxChange={handleCheckboxChange}
        />
      </div>

      <BottomButtonPanel onReset={handleResetConfig} onSave={() => onClose?.()} saveLabel="Close" />

      {activeModal === "labor" && (
        <Modal onClose={() => navigate(null)} allowClickAway={true}>
          <LaborTrackers 
          onClose={() => navigate(null)} 
          onEditTimeBlocks={() => navigate("timeblocks")}
          />
        </Modal>
      )}

      {activeModal === "timeblocks" && (
        <Modal onClose={() => navigate("labor")} allowClickAway={false}>
          <TimeBlocks onClose={() => navigate("labor")}/>
        </Modal>
      )}

      {activeModal === "esh" && (
        <Modal onClose={() => navigate(null)} allowClickAway={false}>
          <ESHAssumptions onClose={() => navigate(null)} />
        </Modal>
      )}

      {activeModal === "rolemap" && (
        <Modal onClose={() => navigate(null)} allowClickAway={false}>
          <RoleMap onClose={() => navigate(null)} />
        </Modal>
      )}

      {activeModal === "saveloc" && (
        <Modal onClose={() => navigate(null)} allowClickAway>
          <SaveLocation onClose={() => navigate(null)} />
        </Modal>
      )}
    </div>
  );
}