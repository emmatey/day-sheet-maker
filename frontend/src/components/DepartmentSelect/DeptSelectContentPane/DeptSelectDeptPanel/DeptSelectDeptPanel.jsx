// /home/emmatey/code/day_sheet_maker/frontend/src/components/DepartmentSelect/DeptSelectContentPane/DeptSelectDeptPanel/DeptSelectDeptPanel.jsx
import "./DeptSelectDeptPanel.css";

export default function DeptSelectDeptPanel({ dept, onToggle, onModeChange }) {
  const { name, selected, mode } = dept;

  return (
    <div
      className={`dept-panel ${selected ? "selected" : ""}`}
      onClick={() => onToggle()}
    >
      {/* Department Name */}
      <div className="dept-title">{name}</div>

      {/* Dropdown + Radio */}
      <div
        className="dept-controls"
        onClick={(e) => e.stopPropagation()} // prevent click from toggling panel when interacting
      >
        <select value={mode} onChange={(e) => onModeChange(Number(e.target.value))}>
          <option value={0}>Table</option>
          <option value={1}>Wall</option>
          <option value={2}>Both</option>
        </select>

        <input
          type="radio"
          checked={selected}
          onChange={() => onToggle()}
        />
      </div>
    </div>
  );
}
