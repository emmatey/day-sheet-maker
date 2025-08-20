// src/components/DepartmentSelect/DeptSelectFooter/DeptSelectFooter.jsx
import { useState } from "react";
import './DeptSelectFooter.css';
import StandardButton from '../../StandardButton/StandardButton.jsx';
import '../../StandardButton/StandardButton.css';
import InfoButton from './../../InfoButton/InfoButton.jsx';
import InfoModal from "../../InfoModal/InfoModal.jsx";

export default function DeptSelectFooter({ onGenerateClick, loading }) {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <>
    <div className = "deptselect-footer">
      {/* Left Section */}
      <div className = "footer-left">
        <div className = "footer-title-card">
          <span>Table, Wall, Both? </span>
        </div>
        <InfoButton 
          onClick = {() => setShowInfo(true)}
          className = 'footer-info-button'
          />
      </div>

      {/* Right Section */}
      <div className = "footer-right">
        <StandardButton
          label = {loading ? "Loading...." : "Generate"}
          onClick = {onGenerateClick}
          disabled = {loading} 
        />
      </div>
    </div>
    
    {/* Info Modal*/}
       <InfoModal
         docUrl = "public/storeLogo.png"
         open = {showInfo}
         onClose = {() => setShowInfo(false)}
       />

    </>
  );
}
