import "./StandardPlusInfoButtonPanel.css";
import StandardButton from "../StandardButton/StandardButton";
import InfoButton from "../InfoButton/InfoButton";

function StandardPlusInfoButtonPanel({
  label,
  onClickMain,
  onClickInfo,
  showInfo = true,
  className = "",         // wrapper
  buttonClassName = "",   // button override
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
        className={`panel-button ${buttonClassName}`}
      />
      {infoEl}
    </div>
  );
}

export default StandardPlusInfoButtonPanel;
