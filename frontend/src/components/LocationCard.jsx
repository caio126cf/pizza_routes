import React, { useState, useEffect } from "react";
import { LocateFixed } from "lucide-react";
import ConfirmLocationCard from "./ConfirmLocationCard";
import DeliveryAddresses from "./DeliveryAddresses";
import { useLoadScript } from "@react-google-maps/api"; // ✅ useLoadScript no lugar de LoadScript
import "./styles/SharedStyles.css";

const libraries = ["places"];

const LocationCard = () => {
  const [address, setAddress] = useState(null);
  const [showCep, setShowCep] = useState(false);
  const [cepInput, setCepInput] = useState("");
  const [step, setStep] = useState("location");

  // ✅ useLoadScript carrega o script de forma controlada e segura
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_API_KEY,
    libraries,
  });

  useEffect(() => {
      if (!isLoaded || step !== "location") return;

    const input = document.getElementById("autocomplete-input");
    if (input && window.google && window.google.maps) {
      const autocomplete = new window.google.maps.places.Autocomplete(input, {
        types: ["geocode"],
        componentRestrictions: { country: "br" },
      });

      autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        if (place && place.formatted_address) {
          setAddress(place.formatted_address);
          setStep("confirm");
        }
      });
    }
    // Opcional: limpar autocomplete ao desmontar
    return () => {
      // Não há método oficial para destruir o autocomplete, mas você pode limpar listeners se quiser
    };
}, [isLoaded, step]);

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

            if (data && data.address && data.address.postcode) {
              const cep = data.address.postcode.replace("-", "");
              const viaCepResponse = await fetch(
                `https://viacep.com.br/ws/${cep}/json/`
              );
              const viaCepData = await viaCepResponse.json();

              if (viaCepData.erro) {
                alert("CEP não encontrado na API ViaCEP.");
                return;
              }

              const fullAddress = `${viaCepData.logradouro}, ${viaCepData.bairro}, ${viaCepData.localidade} - ${viaCepData.uf}`;
              setAddress(fullAddress);
              setStep("confirm");
            } else {
              alert("Não foi possível obter o CEP com base na localização.");
            }
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

  const handleCepChange = async (e) => {
  const value = e.target.value.replace(/\D/g, "");
  setCepInput(value);

  if (value.length === 8) {
    try {
      const response = await fetch(`https://viacep.com.br/ws/${value}/json/`);
      const data = await response.json();
      if (data.erro) {
        alert("CEP não encontrado.");
        return;
      }
      const fullAddress = `${data.logradouro}, ${data.bairro}, ${data.localidade} - ${data.uf}`;
      setAddress(fullAddress);
      setStep("confirm");
    } catch {
      alert("Erro ao buscar o endereço do CEP.");
    }
  }
};

  // ✅ Se erro ao carregar script
  if (loadError) return <div>Erro ao carregar Google Maps</div>;
  // ✅ Se ainda não carregou
  if (!isLoaded) return <div>Carregando mapa...</div>;

  if (step === "confirm") {
    return (
      <ConfirmLocationCard
        address={address}
        onConfirm={() => setStep("delivery")}
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

  if (step === "delivery") {
    return (
      <DeliveryAddresses
        user_location={address}
        onBack={() => setStep("confirm")}
        onNext={() => alert("Endereços enviados com sucesso!")}
      />
    );
  }

  // Etapa inicial
  return (
    <div className="main-card">
      <h2>Encontre sua localização</h2>
      <button className="btn btn-primary" onClick={handleGetLocation}>
        <LocateFixed size={20} className="icon" />
        Capturar Localização
      </button>
      <p className="ou-texto">ou</p>
      <input
        type="text"
        className="input"
        placeholder="Digite o CEP"
        value={cepInput}
        maxLength={8}
        onChange={handleCepChange}
        style={{ marginBottom: 12 }}
      />
      <p className="ou-texto">ou</p>
      <div id="place-autocomplete">
        <input
          id="autocomplete-input"
          type="text"
          placeholder="Digite o endereço"
          className="input"
        />
      </div>
    </div>
  );
};

export default LocationCard;
