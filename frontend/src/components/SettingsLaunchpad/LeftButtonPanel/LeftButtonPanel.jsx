// src/components/SettingsLaunchpad/LeftButtonPanel/LeftButtonPanel.jsx
import "./LeftButtonPanel.css";
import StandardPlusInfoButtonPanel from "../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel";
import { useState } from "react";
import InfoModal from "../../InfoModal/InfoModal";



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
        showInfo = {true}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info"   
      />

      <StandardPlusInfoButtonPanel
        label = "Role Map"
        onClickMain = {onRoleMap}
        onClickInfo = {() => {handleInfoClick("/background.jpg")}}
        showInfo = {true}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info" 
      />

      <StandardPlusInfoButtonPanel
        label = "Labor Trackers"
        onClickMain = {onTimeBlocks}
        onClickInfo = {() => {handleInfoClick("/background.jpg")}}
        showInfo = {true}
        buttonClassName = "settings-launchpad-button"
        infoClassName = "settings-launchpad-info" 
      />

       <StandardPlusInfoButtonPanel
        label = "ESH Assumptions"
        onClickMain = {onEshAssumptions}
        onClickInfo = {() => {handleInfoClick("/background.jpg")}}
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
