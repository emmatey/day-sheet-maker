import './../HomeScreen.css';
import SymbolFrame from './SymbolFrame';
import TitleCard from './TitleCard';

function HeaderFrame() {
  return (
    <div className="header-frame">
      <SymbolFrame />
      <TitleCard />
    </div>
  );
}

export default HeaderFrame;
