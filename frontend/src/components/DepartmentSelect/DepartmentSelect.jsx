// src/components/DepartmentSelect/DepartmentSelect.jsx
import { useState } from "react";
import "./DepartmentSelect.css";
import TitleCardHeader from "./TitleCardHeader/TitleCardHeader.jsx";
import DeptSelectContentPane from "./DeptSelectContentPane/DeptSelectContentPane.jsx";
import DeptSelectFooter from "./DeptSelectFooter/DeptSelectFooter.jsx";

export default function DepartmentSelect({ deptList, inputFile }) {
  // Build initial state: unselected + default Both (index 2)
  const [departments, setDepartments] = useState(
    deptList.map((name) => ({
      name,
      selected: false,
      mode: 2, // 0=Table, 1=Wall, 2=Both
    }))
  );

  const toggleDepartment = (index) => {
    setDepartments((prev) =>
      prev.map((dept, i) =>
        i === index ? { ...dept, selected: !dept.selected } : dept
      )
    );
  };

  const changeMode = (index, newMode) => {
    setDepartments((prev) =>
      prev.map((dept, i) =>
        i === index ? { ...dept, mode: newMode } : dept
      )
    );
  };

  const handleRunPython = async () => {
    try {
      const outputMap = {};
      departments.forEach((dept) => {
        if (dept.selected) {
          outputMap[dept.name] = dept.mode;
        }
      });

      // TODO: replace with settings.json value later
      const saveDir = "/tmp/daysheet_output";

      console.log("Sending to Python:", { inputFile, saveDir, outputMap });

      await window.electronAPI.runPythonOutput({
        inputFile,
        saveDir,
        outputMap,
      });
    } catch (err) {
      console.error("Error running Python output:", err);
    }
  };

  return (
    <div className="department-select-container">
      <TitleCardHeader title = {"Select Departments"} />
      <DeptSelectContentPane
        departments = {departments}
        onToggle = {toggleDepartment}
        onModeChange = {changeMode}
      />
      <DeptSelectFooter onOk = {handleRunPython} />
    </div>
  );
}
