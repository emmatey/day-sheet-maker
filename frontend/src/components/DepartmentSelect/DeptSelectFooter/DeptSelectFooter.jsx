// src/components/DepartmentSelect/DeptSelectFooter/DeptSelectFooter.jsx
import './DeptSelectFooter.css';
import InfoButton from '../../InfoButton/InfoButton.jsx';
import StandardButton from '../../StandardButton/StandardButton.jsx';

export default function DeptSelectFooter({ onInfoClick, onOkClick }) {
  return (
    <div className="deptselect-footer">
      {/* Left Section */}
      <div className="footer-left">
        <div className="footer-title-card">
          Table, Wall, Both -
        </div>
        <InfoButton onClick = {onInfoClick} />
      </div>

      {/* Right Section */}
      <div className="footer-right">
        <StandardButton 
          label="OK" 
          onClick={onOkClick} 
        />
      </div>
    </div>
  );
}
