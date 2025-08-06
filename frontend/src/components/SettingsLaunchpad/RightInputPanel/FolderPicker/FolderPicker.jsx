import "./FolderPicker.css";

export default function FolderPicker({ currentPath, onPick }) {
  return (
    <div className = "folder-picker" onClick = {onPick}>
      <div className = "folder-icon">
        <img src = "/icons/FilePickerOpenButton.svg" alt = "Pick folder" />
      </div>
      <span className = "folder-path">
        {currentPath || "Click to select save location"}
      </span>
    </div>
  );
}
