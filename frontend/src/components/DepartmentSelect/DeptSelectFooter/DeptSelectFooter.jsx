// src/components/DepartmentSelect/DeptSelectFooter/DeptSelectFooter.jsx
import { useState } from "react";
import './DeptSelectFooter.css';
import StandardButton from '../../StandardButton/StandardButton.jsx';
import '../../StandardButton/StandardButton.css';
import InfoButton from './../../InfoButton/InfoButton.jsx';
import InfoModal from "../../InfoModal/InfoModal.jsx";
import Mode_Explanation from "/HelpIconDocs/Mode_Explanation.pdf";

export default function DeptSelectFooter({ onGenerateClick, loading }) {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <>
    <div className = "deptselect-footer">
      <div className = "footer-left">
        <div className = "footer-title-card">
          <span>Table, Wall, Both? </span>
        </div>
        <InfoButton 
          onClick = {() => setShowInfo(true)}
          className = 'footer-info-button'
          />
      </div>

      <div className = "footer-right">
        <StandardButton
          label = {loading ? "Loading...." : "Generate"}
          onClick = {onGenerateClick}
          className = {loading ? "standard-button:disabled" : "standard-button"}
          disabled = {loading} 
        />
      </div>
    </div>
    
       <InfoModal
         docUrl = {Mode_Explanation}
         open = {showInfo}
         onClose = {() => setShowInfo(false)}
       />

    </>
  );
}
