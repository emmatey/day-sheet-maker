// src/components/InfoButton/InfoButton.jsx
import "./InfoButton.css";
import iInfoVector from "/iInfoVector.png";

export default function InfoButton({ onClick, className = "info-button" }) {
  return (
    <button className={`info-button ${className}`} onClick = {onClick}>
      <div className = "outer-ring">
        <div className = "inner-circle">
          <img src={iInfoVector} alt="Info" className="info-icon" />
        </div>
      </div>
    </button>
  );
}
