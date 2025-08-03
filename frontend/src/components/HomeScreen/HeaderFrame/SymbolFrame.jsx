// src/components/HomeScreen/SymbolFrame/SymbolFrame.jsx
import "./../HomeScreen.css";

export default function SymbolFrame({ symbol }) {
  return (
    <div className="symbol-frame">
      <img src={symbol} alt="Symbol" className="store-logo" />
    </div>
  );
}
