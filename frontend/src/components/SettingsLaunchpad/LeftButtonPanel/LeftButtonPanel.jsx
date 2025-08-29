// src/components/SettingsLaunchpad/LeftButtonPanel/LeftButtonPanel.jsx
import "./LeftButtonPanel.css";
import StandardPlusInfoButtonPanel from "../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel";
import { useState } from "react";
import InfoModal from "../../InfoModal/InfoModal";
import roleSetupPdf from "/HelpIconDocs/RoleSetup.pdf";
import eshAssumptionsPdf from "/HelpIconDocs/EshAssumptions.pdf";

export default function LeftButtonPanel({ onSaveLocation, onRoleMap, onTimeBlocks, onEshAssumptions }) {
  const [showInfo, setShowInfo] = useState(false);
  const [docUrl, setDocUrl] = useState("");

  function handleInfoClick(docUrl){
    setDocUrl(docUrl);
    setShowInfo(true);
  };

  return (
    <>
    <div className="left-button-panel">
      <StandardPlusInfoButtonPanel
        label = "Save Location"
        onClickMain = {onSaveLocation}
        onClickInfo = {() => {handleInfoClick("/background.jpg")}}
        showInfo = {false}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info"   
      />

      <StandardPlusInfoButtonPanel
        label = "Role Setup"
        onClickMain = {onRoleMap}
        onClickInfo = {() => {handleInfoClick(roleSetupPdf)}}
        showInfo = {true}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info" 
      />

      <StandardPlusInfoButtonPanel
        label = "Labor Tracking"
        onClickMain = {onTimeBlocks}
        onClickInfo = {() => {handleInfoClick("/background.jpg")}}
        showInfo = {false}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info" 
      />

       <StandardPlusInfoButtonPanel
        label = "ESH Assumptions"
        onClickMain = {onEshAssumptions}
        onClickInfo = {() => {handleInfoClick(eshAssumptionsPdf)}}
        showInfo = {true}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info" 
      />
    </div>

    <InfoModal
    docUrl = {docUrl}
    open = {showInfo}
    onClose = {() => {setShowInfo(false)}}
    />

    </>
  );
}
