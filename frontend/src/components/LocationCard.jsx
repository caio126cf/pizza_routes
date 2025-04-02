import React from "react";
import { MapPin, LocateFixed } from "lucide-react"; // Importando os ícones
import "./LocationCard.css";

const LocationCard = () => {
  return (
    <div className="location-card">
      <h2>Escolha sua localização</h2>
      
      {/* Botão de Capturar Localização */}
      <button className="btn btn-primary">
        <LocateFixed size={20} className="icon" />
        Capturar Localização
      </button>
      
      <p className="ou-texto">ou</p>
      
      {/* Botão de Inserir CEP */}
      <button className="btn btn-outline">
        <MapPin size={20} className="icon" />
        Inserir CEP
      </button>
    </div>
  );
};

export default LocationCard;
