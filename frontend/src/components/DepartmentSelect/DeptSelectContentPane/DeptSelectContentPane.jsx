// /home/emmatey/code/day_sheet_maker/frontend/src/components/DepartmentSelect/DeptSelectContentPane/DeptSelectContentPane.jsx
import "./DeptSelectContentPane.css";
import DeptSelectDeptPanel from "./DeptSelectDeptPanel/DeptSelectDeptPanel.jsx";

export default function DeptSelectContentPane({ departments, toggleDepartment, changeMode }) {
  return (
    <div className="dept-select-content-pane">
      {departments.map((dept) => (
        <DeptSelectDeptPanel
          key={dept.name} // unique key
          dept={dept}     // pass full object
          onToggle={() => toggleDepartment(dept.name)}
          onModeChange={(mode) => changeMode(dept.name, mode)}
        />
      ))}
    </div>
  );
}
