// src/components/HomeScreen/ContentPane/ContentPane.jsx
import { useState } from "react";
import "./../HomeScreen.css";
import SettingsLaunchpad from "../../SettingsLaunchpad/SettingsLaunchpad.jsx";
import StandardPlusInfoButtonPanel from "./../../StandardPlusInfoButtonPannel/StandardPlusInfoButtonPannel.jsx";
import DepartmentSelect from "./../../DepartmentSelect/DepartmentSelect.jsx";
import Modal from "./../../Modal/Modal.jsx";

export default function ContentPane() {
  const [showDeptSelect, setShowDeptSelect] = useState(false);
  const [showSettingsLaunchpad, setShowSettingsLaunchpad] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [filePath, setFilePath] = useState("");

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
          onClickMain = {() => console.log("About clicked")}
          onClickInfo = {() => console.log("Info clicked")}
          showInfo = {false}
        />
      </div>

      {/* Department Select Modal */}
      {showDeptSelect && (
        <Modal onClose={() => setShowDeptSelect(false)}>
          <DepartmentSelect
            deptList = {departments}
            inputFile = {filePath}
            onClose = {() => setShowDeptSelect(false)}
          />
        </Modal>
      )}

      {/* Settings Modal */}
      {showSettingsLaunchpad && (
        <Modal onClose={() => setShowSettingsLaunchpad(false)}>
          <SettingsLaunchpad onClose={() => setShowSettingsLaunchpad(false)} />
        </Modal>
      )}
    </>
  );
}
