// src/components/HomeScreen/HeaderFrame/HeaderFrame.jsx
import "./../HomeScreen.css";
import SymbolFrame from "./SymbolFrame.jsx";
import TitleCard from "./TitleCard.jsx";

export default function HeaderFrame() {
  return (
    <div className="header-frame">
      <SymbolFrame symbol="/storeLogo.png" />
      <TitleCard />
    </div>
  );
}
