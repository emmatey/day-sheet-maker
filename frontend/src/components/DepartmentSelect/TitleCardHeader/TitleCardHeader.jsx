// src/components/DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx
import TitleCard from './../../HomeScreen/HeaderFrame/TitleCard.jsx';
import "./TitleCardHeader.css";

export default function TitleCardHeader({ title }) {
  return (
    <div className = "header-frame-alt">
      <TitleCard title = {title} />
    </div>
  );
}
