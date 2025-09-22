// src/components/HomeScreen/ContentPane/ContentPane.jsx
import { useState } from "react";
import "./../HomeScreen.css";
import SettingsLaunchpad from "../../SettingsLaunchpad/SettingsLaunchpad.jsx";
import StandardPlusInfoButtonPanel from "./../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel.jsx";
import DepartmentSelect from "./../../DepartmentSelect/DepartmentSelect.jsx";
import Modal from "./../../Modal/Modal.jsx";
import InfoModal from "../../InfoModal/InfoModal.jsx";
import startButtonPdf from "/HelpIconDocs/StartButton.pdf";

export default function ContentPane() {
  const [showDeptSelect, setShowDeptSelect] = useState(false);
  const [showSettingsLaunchpad, setShowSettingsLaunchpad] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [filePath, setFilePath] = useState("");
  const [showInfo, setShowInfo] = useState(false);
  const [docUrl, setDocUrl] = useState("");
  const [loading, setLoading] = useState(false);

  function handleInfoClick(docUrl){
    setDocUrl(docUrl);
    setShowInfo(true);
  };

  const handleSelectFile = async () => {
    try {
      const selectedFilePath = await window.electronAPI.selectFile();
      if (!selectedFilePath) {
        console.log("File selection cancelled");
        return;
      }
        setFilePath(selectedFilePath);
        console.log("Selected file:", selectedFilePath);

        setLoading(true);
        const previewResult = await window.electronAPI.runPythonPreview(selectedFilePath);
        setLoading(false);
        const deptList = previewResult
          .split("\n")
          .map(line => line.trim())
          .filter(line => line && !line.startsWith("Log:"));
        console.log("Preview departments:", deptList);

        setDepartments(deptList);
        setShowDeptSelect(true);   
        
    }
    catch (err) {
      console.error(err);
      setLoading(false);
    }
  };
  
  const handleAboutClick = () => {
    const windowFeatures = "width = 1000, height = 900";
    const URL = "https://github.com/emmatey/day-sheet-maker";
    window.open(URL, "_blank", windowFeatures);
  };

  return (
    <>
      <div className="content-pane">
        <StandardPlusInfoButtonPanel
          label = {loading ? "Reading File..." : "Start"}
          onClickMain = {handleSelectFile}
          onClickInfo = {() => {handleInfoClick(startButtonPdf)}}
          showInfo = {true}
          buttonClassName = {loading ? "standard-button:disabled" : "home-screen-button"}
          stdButtonDisabled = {loading ? true : false}
        />
        <StandardPlusInfoButtonPanel
          label = "Settings"
          onClickMain = {() => setShowSettingsLaunchpad(true)}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {false}
          buttonClassName = "home-screen-button"
        />
        <StandardPlusInfoButtonPanel
          label = "About"
          onClickMain = {handleAboutClick}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {false}
          buttonClassName = "home-screen-button"
        />
      </div>

      {/* Department Select Modal */}
      {showDeptSelect && (
        <Modal onClose={() => setShowDeptSelect(false)} allowClickAway = {true}>
          <DepartmentSelect
            deptList = {departments}
            inputFile = {filePath}
            onClose = {() => setShowDeptSelect(false)}
          />
        </Modal>
      )}

      {showSettingsLaunchpad && (
        <Modal
          onClose={() => setShowSettingsLaunchpad(false)}
          allowClickAway = {true}>
          <SettingsLaunchpad
            onClose={() => setShowSettingsLaunchpad(false)} />
        </Modal>
      )}
  
      <InfoModal
        docUrl = {docUrl}
        open = {showInfo}
        onClose = {() => setShowInfo(false)}
      />
    
    </>
  );
}
