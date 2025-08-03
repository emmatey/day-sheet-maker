// src/components/HomeScreen/ContentPane/ContentPane.jsx
import { useState } from "react";
import "./../HomeScreen.css";
import StandardPlusInfoButtonPanel from "./../../StandardPlusInfoButtonPannel/StandardPlusInfoButtonPannel.jsx";

export default function ContentPane() {
  const handleSelectFile = async () => {
    try {
      const filePath = await window.electronAPI.selectFile();
      if (filePath) {
        const deptList = await window.electronAPI.runPythonPreview(filePath);
        console.log(deptList);
      } else {
        console.log("File selection cancelled");
      }
    } catch (err) {
      console.error("Error selecting file:", err);
    }
  };

  return (
    <div className="content-pane">
      <StandardPlusInfoButtonPanel
        label="Start"
        onClickMain={handleSelectFile}
        onClickInfo={() => console.log("Info clicked")}
        showInfo={true}
      />
      <StandardPlusInfoButtonPanel
        label="Settings"
        onClickMain={() => console.log("Settings clicked")}
        onClickInfo={() => console.log("Info clicked")}
        showInfo={false}
      />
      <StandardPlusInfoButtonPanel
        label="About"
        onClickMain={() => console.log("About clicked")}
        onClickInfo={() => console.log("Info clicked")}
        showInfo={false}
      />
    </div>
  );
}
