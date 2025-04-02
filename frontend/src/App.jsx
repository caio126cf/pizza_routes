import React from "react";
import Header from "./components/Header";
import LocationCard from "./components/LocationCard";
import Footer from "./components/Footer";

function App() {
  return (
    <div>
      <Header />
      <main>
        <LocationCard />
      </main>
      <Footer />
    </div>
  );
}

export default App;
