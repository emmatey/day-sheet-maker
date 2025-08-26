// src/components/InfoModal/InfoModal.jsx
import Modal from "../Modal/Modal";
import StandardButton from "../StandardButton/StandardButton";
import "./InfoModal.css";

export default function InfoModal({ docUrl, open, onClose }) {
  if (!open) return null;

  const isPdf = /\.pdf(\?|$)/i.test(docUrl);
  const isImg = /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(docUrl);

  // Hide Chrome's PDF chrome & fit page
  const pdfSrc = isPdf
    ? `${docUrl}#toolbar=0&navpanes=0&scrollbar=0&zoom=125%`
    : docUrl;

  return (
    <Modal onClose={onClose} allowClickAway={true}>
      <div className="info-modal">
        {isImg ? (
          <img src={docUrl} alt="Info document" className="info-image" />
        ) : (
          <iframe src={pdfSrc} className="info-frame" title="Info Document" />
        )}

        <div className="info-close-button">
          <StandardButton label="Close" onClick={onClose} />
        </div>
      </div>
    </Modal>
  );
}
