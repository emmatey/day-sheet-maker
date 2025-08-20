// src/components/HomeScreen/ContentPane/ContentPane.jsx
import { useState } from "react";
import "./../HomeScreen.css";
import SettingsLaunchpad from "../../SettingsLaunchpad/SettingsLaunchpad.jsx";
import StandardPlusInfoButtonPanel from "./../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel.jsx";
import DepartmentSelect from "./../../DepartmentSelect/DepartmentSelect.jsx";
import Modal from "./../../Modal/Modal.jsx";
import InfoModal from "../../InfoModal/InfoModal.jsx";

export default function ContentPane() {
  const [showDeptSelect, setShowDeptSelect] = useState(false);
  const [showSettingsLaunchpad, setShowSettingsLaunchpad] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [filePath, setFilePath] = useState("");
  //const setshowinfo? 

  const handleSelectFile = async () => {
    try {
      const selectedFilePath = await window.electronAPI.selectFile();
      if (!selectedFilePath) {
        console.log("File selection cancelled");
        return;
      }
      setFilePath(selectedFilePath);
      console.log("Selected file:", selectedFilePath);

      const previewResult = await window.electronAPI.runPythonPreview(selectedFilePath);

      const deptList = previewResult
        .split("\n")
        .map(line => line.trim())
        .filter(line => line && !line.startsWith("Log:"));

      console.log("Preview departments:", deptList);

      setDepartments(deptList);
      setShowDeptSelect(true);
    } catch (err) {
      console.error("Error selecting file or running preview:", err);
    }
  };
  
  const handleAboutClick = () => {
    //URL = "https://github.com/emmatey/day-sheet-maker";
    const windowFeatures = "width = 1000, height = 900";
    URL = "https://github.com/";
    onclick(window.open(URL, "_blank", windowFeatures));
  };

  return (
    <>
      <div className="content-pane">
        <StandardPlusInfoButtonPanel
          label = "Start"
          onClickMain = {handleSelectFile}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {true}
        />
        <StandardPlusInfoButtonPanel
          label = "Settings"
          onClickMain = {() => setShowSettingsLaunchpad(true)}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {false}
        />
        <StandardPlusInfoButtonPanel
          label = "About"
          onClickMain = {handleAboutClick}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {false}
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

      {/* Settings Modal */}
      {showSettingsLaunchpad && (
        <Modal onClose={() => setShowSettingsLaunchpad(false)} allowClickAway = {true}>
          <SettingsLaunchpad onClose={() => setShowSettingsLaunchpad(false)} />
        </Modal>
      )}
    </>
  );
}
