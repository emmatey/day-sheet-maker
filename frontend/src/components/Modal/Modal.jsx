// Modal.jsx
import React from "react";
import ReactDOM from "react-dom";
import TitleCardHeader from "@/components/DepartmentSelect/TitleCardHeader/TitleCardHeader.jsx";

export default function Modal({
  isOpen,
  title,                // <- pass the panel title here
  children,
  onSaveAndClose,
  onCancel,
  footerVariant = "standard",  // "standard" | "dismiss" | "none"
  closeOnEsc = false,
  closeOnOverlayClick = false,
}) {
  React.useEffect(() => {
    if (!isOpen) return;
    const handler = (e) => {
      if (e.key === "Escape") {
        if (!closeOnEsc) e.preventDefault();
        else onCancel?.();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isOpen, closeOnEsc, onCancel]);

  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div
      className="ModalOverlay"
      onClick={closeOnOverlayClick ? onCancel : undefined}
    >
      <div
        className="ModalCard"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="ModalHeader">
          <TitleCardHeader title={title} />
        </div>

        <div className="ModalBody">{children}</div>

        {footerVariant !== "none" && (
          <div className="ModalFooter">
            {footerVariant === "standard" ? (
              <>
                <button className="btn secondary" onClick={onCancel}>Cancel</button>
                <div className="spacer" />
                <button className="btn primary" onClick={onSaveAndClose}>Save &amp; Close</button>
              </>
            ) : (
              <div className="end">
                <button className="btn primary" onClick={onCancel}>Close</button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}
