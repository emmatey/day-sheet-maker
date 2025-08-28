// src/components/HomeScreen/HeaderFrame/HeaderFrame.jsx
import "./../HomeScreen.css";
import SymbolFrame from "./SymbolFrame.jsx";
import TitleCard from "./TitleCard.jsx";
import storeLogo from "/storeLogo.png";

export default function HeaderFrame() {
  return (
    <div className="header-frame">
      <SymbolFrame symbol={storeLogo} />
      <TitleCard title="Day Sheet Maker" />
    </div>
  );
}
