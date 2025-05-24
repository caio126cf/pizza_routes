import React from "react";
import Header from "./components/Header";
import LocationCard from "./components/LocationCard";
import Footer from "./components/Footer";
import "./App.css";


function App() {

  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <LocationCard />
      </main>
      <Footer />
    </div>
  );
}

export default App;
