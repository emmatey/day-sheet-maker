// src/components/HomeScreen/HomeScreen.jsx
import "./HomeScreen.css";
import HeaderFrame from "./HeaderFrame/HeaderFrame";
import ContentPane from "./ContentPane/ContentPane";
import AccentStripe from "./AccentStripe/AccentStripe";

export default function HomeScreen() {
  return (
    <div className="home-screen">
      <HeaderFrame />
      <AccentStripe />
      <ContentPane />
    </div>
  );
}
