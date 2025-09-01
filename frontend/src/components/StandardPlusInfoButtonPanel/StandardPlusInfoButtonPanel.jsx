import "./StandardPlusInfoButtonPanel.css";
import StandardButton from "../StandardButton/StandardButton";
import InfoButton from "../InfoButton/InfoButton";
import "../StandardButton/StandardButton.css";

function StandardPlusInfoButtonPanel({
  label,
  onClickMain,
  onClickInfo,
  showInfo = true,
  className = "",         // wrapper
  buttonClassName = "",   // button override
  stdButtonDisabled = false,
  infoClassName = "",     // info-button override
}) {
  const infoEl = showInfo ? (
    <InfoButton
      onClick={onClickInfo}
      className={`info-button-panel-style ${infoClassName}`}
    />
  ) : null;

  return (
    <div className={`standard-plus-info-panel ${className}`}>
      <StandardButton
        label={label}
        onClick={onClickMain}
        className={`standard-button ${buttonClassName}`}
        stdButtonDisabled={stdButtonDisabled}
      />
      {infoEl}
    </div>
  );
}

export default StandardPlusInfoButtonPanel;
