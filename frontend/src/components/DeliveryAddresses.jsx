import React, { useState, useRef, useEffect } from "react";
import { MapPin, Trash, CheckCircle } from "lucide-react";
import { useLoadScript } from "@react-google-maps/api";
import "./styles/SharedStyles.css";
import { Image } from "lucide-react";

const libraries = ["places"];

const DeliveryAddresses = ({ onBack, onNext, user_location}) => {
  const [inputValue, setInputValue] = useState("");
  const [addresses, setAddresses] = useState([]);
  const [mode, setMode] = useState("default");
  const [bulkInput, setBulkInput] = useState("");

  const textareaRefs = useRef([]);
  const inputRef = useRef(null); // 🔹 Usado para apontar para o campo com autocomplete

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_API_KEY,
    libraries,
  });

    const handleContinue = async () => {
      if (!user_location) {
        alert("Localização do usuário não definida.");
        return;
      }
      if (addresses.length === 0) {
        alert("Adicione pelo menos um endereço de entrega.");
        return;
      }

      try {
        const formData = new FormData();
        formData.append("user_location", user_location);
        formData.append("delivery_addresses", JSON.stringify(addresses));

        const response = await fetch("http://localhost:8000/api/delivery-route/", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          alert("Rota otimizada criada com sucesso!");
          if (onNext) onNext(data);
        } else {
          alert(data.error || "Erro ao criar rota.");
        }
      } catch (err) {
        alert("Erro ao conectar ao backend.");
      }
    };

  useEffect(() => {
    if (!isLoaded || !inputRef.current || !window.google) return;

    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
      types: ["geocode"],
      componentRestrictions: { country: "br" },
    });

    autocomplete.addListener("place_changed", () => {
      const place = autocomplete.getPlace();
      if (place && place.formatted_address) {
        setAddresses((prev) => [...prev, place.formatted_address]);
        setInputValue(""); // Limpa o campo após adicionar
      }
    });
  }, [isLoaded]);

  useEffect(() => {
    textareaRefs.current.forEach((ref) => {
      if (ref) {
        ref.style.height = "auto";
        ref.style.height = `${ref.scrollHeight}px`;
      }
    });
  }, [addresses]);


  const handleAddBulkAddresses = () => {
    const list = bulkInput
      .split("\n")
      .map((a) => a.trim())
      .filter(Boolean);
    setAddresses([...addresses, ...list]);
    setBulkInput("");
    setMode("default");
  };

  const handleCancelBulk = () => {
    setBulkInput("");
    setMode("default");
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0]; // Obtém o arquivo selecionado
  
    // Verifica se um arquivo foi selecionado
    if (!file) {
      alert("Nenhuma imagem selecionada.");
      return;
    }
  
    // Sanitização: verifica o tipo do arquivo
    const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!allowedTypes.includes(file.type)) {
      alert("Formato de arquivo inválido. Apenas JPEG e PNG são permitidos.");
      return;
    }
  
    // Sanitização: verifica o tamanho do arquivo (limite de 5MB)
    const maxSize = 10485760; // 10MB
    if (file.size > maxSize) {
      alert("O arquivo é muito grande. O tamanho máximo permitido é 5MB.");
      return;
    }
    alert("O arquivo subiu!")
  
    // Cria um FormData para enviar o arquivo
    const formData = new FormData();
    formData.append("image", file);
  
    try {
      // Faz a requisição POST para o backend
      const response = await fetch("http://localhost:8000/api/image-extract/", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error("Erro ao enviar a imagem. Tente novamente.");
      }
  
      const json = await response.json();
      if (Array.isArray(json.data)) {
        // Adiciona os endereços extraídos à lista
        setAddresses((prev) => [...prev, ...json.data]);
        alert("Endereços extraídos com sucesso!");
      } else {
        alert("Nenhum endereço foi extraído da imagem.");
      }
    } catch (error) {
      console.error("Erro ao enviar a imagem:", error);
      alert("Erro ao processar a imagem. Tente novamente.");
    }
  };

  const handleDeleteAddress = (index) => {
    const updated = addresses.filter((_, i) => i !== index);
    setAddresses(updated);
  };

  if (loadError) return <div>Erro ao carregar Google Maps</div>;
  if (!isLoaded) return <div>Carregando autocomplete...</div>;

  return (
    <div className="main-card">
      <h2 className="delivery-header">
        <MapPin size={24} />
        Endereços de entrega
      </h2>

      {mode === "default" ? (
        <>
          <div className="delivery-input-row">
            <input
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="input"
              placeholder="Digite um endereço de entrega"
            />
          </div>
          <p className="ou-texto">ou</p>
          <div className="delivery-buttons-row">
                <label className="btn btn-outline">
                  <Image size={25} /> Enviar imagem
                  <input
                    type="file"
                    accept="image/jpeg, image/png"
                    style={{ display: "none" }}
                    onChange={handleImageUpload}
                  />
                </label>
          </div>
        </>
      ) : (
        <>
          <textarea
            className="input delivery-textarea bulk"
            rows={4}
            value={bulkInput}
            onChange={(e) => setBulkInput(e.target.value)}
            placeholder="Cole aqui os endereços, um por linha"
          />
          <div className="delivery-buttons-row">
            <button className="btn btn-primary" onClick={handleAddBulkAddresses}>
              Adicionar endereços
            </button>
            <button className="btn btn-outline" onClick={handleCancelBulk}>
              Cancelar
            </button>
          </div>
        </>
      )}

      {addresses.length > 0 && (
        <>
          <h2 className="delivery-header">
            <CheckCircle size={24} />
            Endereços adicionados
          </h2>
          <div className="delivery-addresses-list">
            {addresses.map((addr, idx) => (
              <div key={idx} className="delivery-address-item">
                <textarea
                  value={addr}
                  readOnly
                  className="input delivery-address-textarea"
                  rows={1}
                  ref={(el) => (textareaRefs.current[idx] = el)}
                />
                <button
                  className="btn btn-icon"
                  onClick={() => handleDeleteAddress(idx)}
                >
                  <Trash size={24} />
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="delivery-actions-row">
        <button className="btn btn-outline" onClick={onBack}>
          Voltar
        </button>
        <button className="btn btn-primary" onClick={handleContinue}>
          Continuar
        </button>
      </div>
    </div>
  );
};

export default DeliveryAddresses;
