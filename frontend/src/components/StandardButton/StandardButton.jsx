// src/components/StandardButton/StandardButton.jsx
export default function StandardButton({ 
  label, 
  onClick, 
  className = "", 
  disabled = false, 
  ...rest
}) {
  return (
    <button 
      className={`standard-button ${className}`} 
      onClick = {onClick} 
      disabled = {disabled} 
      {...rest}
    >
      {label}
    </button>
  );
}
