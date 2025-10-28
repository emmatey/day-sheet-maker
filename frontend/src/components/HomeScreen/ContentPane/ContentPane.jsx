// src/components/HomeScreen/ContentPane/ContentPane.jsx
import { useState } from "react";
import "./../HomeScreen.css";
import SettingsLaunchpad from "../../SettingsLaunchpad/SettingsLaunchpad.jsx";
import StandardPlusInfoButtonPanel from "./../../StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel.jsx";
import DepartmentSelect from "./../../DepartmentSelect/DepartmentSelect.jsx";
import Modal from "./../../Modal/Modal.jsx";
import { filterError } from "./../../../utils/FilterError.js"

export default function ContentPane() {
  const [showDeptSelect, setShowDeptSelect] = useState(false);
  const [showSettingsLaunchpad, setShowSettingsLaunchpad] = useState(false);
  const [departments, setDepartments] = useState([]);
  const [filePath, setFilePath] = useState("");
  const [loading, setLoading] = useState(false);

  const handleStartButtonInfoClick = () => {
    window.electronAPI.nativeAlert({
      message: "To begin, select the input file\nThis must be the weekly schedule exported from Kronos in either .xlsx or .csv format\n(PDF Files are not supported!)",
      type: "info"
    })
  };

  const handleAboutClick = () => {
    const windowFeatures = "width = 1000, height = 900";
    const URL = "https://github.com/emmatey/day-sheet-maker";
    window.open(URL, "_blank", windowFeatures);
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
      const filtered_error = filterError(err);
      window.electronAPI.nativeAlert({
        message: filtered_error,
        type: "error",
      });
      setLoading(false);
    }
  };

  return (
    <>
      <div className="content-pane">
        <StandardPlusInfoButtonPanel
          label = {loading ? "Reading File..." : "Upload Schedule"}
          onClickMain = {handleSelectFile}
          onClickInfo = {handleStartButtonInfoClick}
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
    </>
  );
}
