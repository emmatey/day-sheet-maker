// src/components/HomeScreen/HomeScreen.tsx
import './HomeScreen.css';
import HeaderFrame from './HeaderFrame/HeaderFrame';
import ContentPane from './ContentPane/ContentPane';
import AccentStripe from './AccentStripe/AccentStripe';

function HomeScreen() {
  return (
    <div className="home-screen">
      <HeaderFrame />
      <AccentStripe />
      <ContentPane />
    </div>
  );
}

export default HomeScreen;
