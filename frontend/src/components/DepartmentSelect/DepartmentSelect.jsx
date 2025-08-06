import { useState } from "react";
import "./DepartmentSelect.css";
import TitleCardHeader from "./TitleCardHeader/TitleCardHeader.jsx";
import AccentStripe from "./../HomeScreen/AccentStripe/AccentStripe.jsx";
import DeptSelectContentPane from "./DeptSelectContentPane/DeptSelectContentPane.jsx";
import DeptSelectFooter from "./DeptSelectFooter/DeptSelectFooter.jsx";

export default function DepartmentSelect({ deptList, inputFile, onClose }) {
  const [departments, setDepartments] = useState(
    deptList.map((name) => ({
      name,
      selected: false,
      mode: 2,
    }))
  );

  const [loading, setLoading] = useState(false);

  const toggleDepartment = (index) => {
    setDepartments((previousDepartments) => {
      const updatedDepartments = previousDepartments.map((department, currentIndex) => {
        if (currentIndex === index) {
          return {
            ...department,
            selected: !department.selected,
          };
        }
        return department;
      });
      return updatedDepartments;
    });
  };

  const changeMode = (index, newMode) => {
    setDepartments((previousDepartments) => {
      const updatedDepartments = previousDepartments.map((department, currentIndex) => {
        if (currentIndex === index) {
          return {
            ...department,
            mode: newMode,
          };
        }
        return department;
      });
      return updatedDepartments;
    });
  };

  const handleRunPython = async () => {
    try {
      setLoading(true); // Start loading

      const outputMap = {};
      departments.forEach((dept) => {
        if (dept.selected) {
          outputMap[dept.name] = dept.mode;
        }
      });

      const saveDir = "/tmp/daysheet_output"; // TODO: from settings.json

      console.log("Sending to Python:", { inputFile, saveDir, outputMap });

      await window.electronAPI.runPythonOutput({
        inputFile,
        saveDir,
        outputMap,
      });

      // Open the save folder
      await window.electronAPI.openFolder(saveDir);

      setLoading(false);
      onClose?.(); // Close modal
    } catch (err) {
      setLoading(false);
      console.error("Error running Python output:", err);
    }
  };

  return (
    <div
      className = "department-select-container"
      style = {{ cursor: loading ? "wait" : "default" }}
    >
      <TitleCardHeader title = "Select Departments" />
      <AccentStripe />
      <DeptSelectContentPane
        departments = {departments}
        toggleDepartment = {toggleDepartment}
        changeMode = {changeMode}
      />
      <DeptSelectFooter
        onGenerateClick = {handleRunPython}
        loading = {loading}
      />
    </div>
  );
}