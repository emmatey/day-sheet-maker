// src/components/HomeScreen/HomeScreen.jsx
import { useEffect } from "react";
import "./HomeScreen.css";
import HeaderFrame from "./HeaderFrame/HeaderFrame";
import ContentPane from "./ContentPane/ContentPane";
import AccentStripe from "./AccentStripe/AccentStripe";

export default function HomeScreen() {
  useEffect(() => {
    (async () => {
      try {
        const cfg = await window.electronAPI.readSettings();
        console.log("Loaded settings:", cfg);
      } catch (e) {
        console.error("readSettings (HomeScreen) failed:", e);
      }
    })();
  }, []);

  return (
    <div className="home-screen">
      <HeaderFrame />
      <AccentStripe />
      <ContentPane />
    </div>
  );
}
