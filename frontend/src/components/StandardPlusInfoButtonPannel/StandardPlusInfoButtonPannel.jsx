// src/components/StandardPlusInfoButtonPanel/StandardPlusInfoButtonPanel.jsx
import "./StandardPlusInfoButtonPannel.css";
import StandardButton from "../StandardButton/StandardButton";
import InfoButton from "../InfoButton/InfoButton";

function StandardPlusInfoButtonPanel({
  label,
  onClickMain,
  onClickInfo,
  showInfo = true,
}) {
  let infoButtonElement = null;

  if (showInfo === true) {
    infoButtonElement = (
      <InfoButton onClick={onClickInfo} className="info-button-panel-style" />
    );
  }

  return (
    <div className="standard-plus-info-panel">
      <StandardButton
        label={label}
        onClick={onClickMain}
        className="panel-button"
      />
      {infoButtonElement}
    </div>
  );
}

export default StandardPlusInfoButtonPanel;
