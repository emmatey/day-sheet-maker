// src/components/InfoModal/InfoModal.jsx
import Modal from "../Modal/Modal";
import StandardButton from "../StandardButton/StandardButton";
import "./InfoModal.css";

// InfoModal displays a document inside a modal.
// docUrl should point to a file in the public folder (e.g. /docs/myDoc.pdf)
export default function InfoModal({ docUrl, open, onClose }) {
  if (!open) return null;

  return (
    <Modal onClose = {onClose} allowClickAway = {true}>
      <div className = "info-modal">
        <iframe src = {docUrl} className = "info-frame" title = "Info Document" />
        <div className = "info-close-button">
          <StandardButton label = "Close" onClick={onClose} />
        </div>
      </div>
    </Modal>
  );
}