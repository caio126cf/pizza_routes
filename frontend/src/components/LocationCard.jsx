import React, { useState } from "react";
import { LocateFixed } from "lucide-react";
import ConfirmLocationCard from "./ConfirmLocationCard";
import DeliveryAddresses from "./DeliveryAddresses"; // Importa o novo componente
import "./styles/LocationCard.css";

const LocationCard = () => {
  const [address, setAddress] = useState(null);
  const [showCep, setShowCep] = useState(false);
  const [step, setStep] = useState("location"); // "location", "confirm", "delivery"

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
            );
            const data = await response.json();
            setAddress(data.display_name);
            setStep("confirm");
          } catch (error) {
            alert("Erro ao obter endereço!");
          }
        },
        () => alert("Permissão negada! Ative a localização no navegador.")
      );
    } else {
      alert("Geolocalização não suportada.");
    }
  };

  // Etapa: confirmação do endereço
  if (step === "confirm") {
    return (
      <ConfirmLocationCard
        address={address}
        onConfirm={() => setStep("delivery")} // Agora redireciona para DeliveryAddresses
        onReject={() => {
          setAddress(null);
          setShowCep(false);
          setStep("location");
        }}
        onEdit={() => setStep("location")}
        viaCep={showCep}
        setAddress={setAddress}
      />
    );
  }

  // Etapa: adicionar endereços de entrega
  if (step === "delivery") {
    return (
      <DeliveryAddresses
        onBack={() => setStep("confirm")}
        onNext={() => alert("Endereços enviados com sucesso!")}
      />
    );
  }

  // Etapa inicial
  return (
    <div className="location-card">
      <h2>Escolha sua localização</h2>
      <button className="btn btn-primary" onClick={handleGetLocation}>
        <LocateFixed size={20} className="icon" />
        Capturar Localização
      </button>
      <p className="ou-texto">ou</p>
      <button className="btn btn-outline" onClick={() => {
        setShowCep(true);
        setStep("confirm");
      }}>
        Inserir CEP
      </button>
    </div>
  );
};

export default LocationCard;
