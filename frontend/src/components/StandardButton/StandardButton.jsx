// src/components/StandardButton/StandardButton.jsx
export default function StandardButton({ label, onClick, className = "" }) {
  return (
    <button className = {`standard-button ${className}`} onClick = {onClick}>
      {label}
    </button>
  );
}
