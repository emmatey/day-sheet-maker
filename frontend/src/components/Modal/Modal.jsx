// src/components/Modal/Modal.jsx
import "./Modal.css";

export default function Modal({ children, onClose, allowClickAway = true }) {
  const handleOverlayClick = () => {
    if (allowClickAway) onClose?.();
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}