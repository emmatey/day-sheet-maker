// src/components/DepartmentSelect/DeptSelectFooter/DeptSelectFooter.jsx
import './DeptSelectFooter.css';
import StandardButton from '../../StandardButton/StandardButton.jsx';
import '../../StandardButton/StandardButton.css';
import InfoButton from './../../InfoButton/InfoButton.jsx';

export default function DeptSelectFooter({ onGenerateClick, loading }) {
  return (
    <div className = "deptselect-footer">
      {/* Left Section */}
      <div className = "footer-left">
        <div className = "footer-title-card">
          <span>Table, Wall, Both? </span>
        </div>
        <InfoButton className = 'footer-info-button'/>
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
  );
}
