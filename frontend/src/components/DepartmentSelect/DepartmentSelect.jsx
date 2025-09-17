import { useState, useEffect } from "react";
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
  const [saveDir, setSaveDir] = useState("");

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        if (!alive) return;
        const path = cfg?.SAVE_LOCATION?.save_location_string || "";
        setSaveDir(path);
      } catch (e) {
        console.error("readSettings (DepartmentSelect) failed:", e);
      }
    })();
    return () => { alive = false; };
  }, []);

  const toggleDepartment = (index) => {
    setDepartments((prev) =>
      prev.map((d, i) => (i === index ? { ...d, selected: !d.selected } : d))
    );
  };

  const changeMode = (index, newMode) => {
    setDepartments((prev) =>
      prev.map((d, i) => (i === index ? { ...d, mode: newMode } : d))
    );
  };

  const handleRunPython = async () => {
  try {
    setLoading(true); 

    const outputMap = {};
    departments.forEach((dept) => {
      if (dept.selected) {
        outputMap[dept.name] = dept.mode;
      }
    });

    let outDir = saveDir;
    if (!outDir) {
      const picked = await window.electronAPI.selectDirectory();
      if (!picked) {
        setLoading(false);
        return; // user canceled
      }
      outDir = picked;
      setSaveDir(picked);
    }
    console.log("Sending to Python:", { inputFile, saveDir, outputMap });

    await window.electronAPI.runPythonOutput({
      inputFile,
      saveDir,
      outputMap,
    });

    setTimeout(() => {
      window.electronAPI.openFolder(saveDir).catch(() => {});
    }, 0);

    setLoading(false);
    onClose();

  } catch (err) {
    setLoading(false);
    console.error("--[Error running Python output]--\n", err);
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