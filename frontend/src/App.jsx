import "./App.css";
import HomeScreen from "./components/HomeScreen/HomeScreen.jsx";
import bgUrl from "/background.jpg";            // from frontend/public

export default function App() {
  return (
    <div className="app-background" style={{ backgroundImage: `url(${bgUrl})` }}>
      <HomeScreen />
    </div>
  );
}
