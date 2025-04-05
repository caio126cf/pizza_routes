import React from "react";
import { Route } from "lucide-react";
import "./styles/Header.css"; // Importa o CSS

const Header = () => {
  return (
    <header className="header">
      <Route size={32} className="icon" />
      <h1>Otimiza Rotas</h1>
    </header>
  );
};

export default Header;