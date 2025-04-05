import React, { useState, useRef, useEffect } from "react";
import { MapPin, Plus, Trash } from "lucide-react";
import "./styles/DeliveryAddresses.css";

const DeliveryAddresses = ({ onBack, onNext }) => {
  const [inputValue, setInputValue] = useState("");
  const [addresses, setAddresses] = useState([]);
  const [mode, setMode] = useState("default");
  const [bulkInput, setBulkInput] = useState("");

  const textareaRefs = useRef([]);

  useEffect(() => {
    textareaRefs.current.forEach((ref) => {
      if (ref) {
        ref.style.height = "auto";
        ref.style.height = `${ref.scrollHeight}px`;
      }
    });
  }, [addresses]);

  const handleAddSingleAddress = () => {
    if (inputValue.trim()) {
      setAddresses([...addresses, inputValue.trim()]);
      setInputValue("");
    }
  };

  const handlePasteAddresses = () => {
    setMode("bulk");
  };

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

  const handleImageUpload = () => {
    alert("Funcionalidade de envio de imagem será implementada.");
  };

  const handleDeleteAddress = (index) => {
    const updated = addresses.filter((_, i) => i !== index);
    setAddresses(updated);
  };

  return (
    <div className="confirm-card">
      <h2>
        <MapPin size={24} className="icon-title" />
        Endereços de entrega
      </h2>

      {mode === "default" ? (
        <>
          <div className="delivery-input-row">
            <textarea
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = `${e.target.scrollHeight}px`;
              }}
              className="delivery-textarea"
              placeholder="Digite um endereço de entrega"
              rows={1}
            />
            <button
              className="btn btn-primary btn-icon"
              onClick={handleAddSingleAddress}
            >
              <Plus size={16} />
            </button>
          </div>

          <div className="delivery-buttons-row">
            <button className="btn btn-outline" onClick={handlePasteAddresses}>
              Adicionar vários endereços
            </button>
            <button className="btn btn-outline" onClick={handleImageUpload}>
              Enviar imagem
            </button>
          </div>
        </>
      ) : (
        <>
          <textarea
            className="delivery-textarea"
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
          <h3>Endereços adicionados</h3>
          <div className="addresses-list">
            {addresses.map((addr, idx) => (
              <div key={idx} className="address-item">
                <textarea
                  value={addr}
                  readOnly
                  className="added-address-textarea"
                  rows={1}
                  onFocus={(e) => {
                    e.target.style.height = "auto";
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                  onInput={(e) => {
                    e.target.style.height = "auto";
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                />
                <Trash
                  size={16}
                  className="icon delete-icon"
                  onClick={() => handleDeleteAddress(idx)}
                />
              </div>
            ))}
          </div>
        </>
      )}

      <div className="actions-row">
        <button className="btn btn-outline" onClick={onBack}>
          Voltar
        </button>
        <button className="btn btn-primary" onClick={onNext}>
          Continuar
        </button>
      </div>
    </div>
  );
};

export default DeliveryAddresses;
