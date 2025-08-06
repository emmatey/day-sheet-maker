// /home/emmatey/code/day_sheet_maker/frontend/src/components/DepartmentSelect/DeptSelectContentPane/DeptSelectContentPane.jsx
import "./DeptSelectContentPane.css";
import DeptSelectDeptPanel from "./DeptSelectDeptPanel/DeptSelectDeptPanel.jsx";

export default function DeptSelectContentPane({ departments, toggleDepartment, changeMode }) {
  return (
    <div className="dept-select-content-pane">
      {departments.map((dept, index) => (
        <DeptSelectDeptPanel
          key = {dept.name}
          dept = {dept}
          onToggle = {() => toggleDepartment(index)}
          onModeChange = {(mode) => changeMode(index, mode)}
        />
      ))}
    </div>
  );
}