import React, { useState, useRef, useEffect } from "react";
import { MapPin, CheckCircle, XCircle, MailCheck, Pencil } from "lucide-react";
import "./styles/ConfirmLocationCard.css";

const ConfirmLocationCard = ({ address, onConfirm, onReject, onEdit, viaCep, setAddress }) => {
  const [cep, setCep] = useState("");
  const [isEditing, setIsEditing] = useState(false); // <--- novo estado

  const handleGetCep = async () => {
    const cleanCep = cep.replace(/\D/g, ""); // remove tudo que não for número

    if (cleanCep.length !== 8) {
      alert("Digite um CEP válido com 8 dígitos.");
      return;
    }

    try {
      const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
      const data = await response.json();

      if (data.erro) {
        alert("CEP não encontrado.");
        return;
      }

      const fullAddress = `${data.logradouro}, ${data.bairro}, ${data.localidade} - ${data.uf}`;
      setAddress(fullAddress);
    } catch (error) {
      alert("Erro ao buscar o CEP.");
    }
  };
  const textareaRef = useRef(null);

  // Atualiza a altura do textarea automaticamente ao mudar o endereço
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [address]);
  const handleEditToggle = () => {
    setIsEditing(true); // entra em modo de edição
  };

  return (
    <div className="confirm-card">
      <h2>
        <MapPin size={24} className="icon-title" />
        Confirmar Endereço
      </h2>

      {!address && viaCep && (
        <div className="cep-container">
              <input
                type="text"
                placeholder="Digite o CEP (ex: 01001000 ou 01001-000)"
                value={cep}
                onChange={(e) => {
                  // Aceita hífen visualmente, mas remove caracteres inválidos para armazenar
                  const raw = e.target.value.replace(/[^0-9-]/g, "");
                  setCep(raw);
                }}
                className="cep-input"
                maxLength={9} // 8 números + 1 hífen
              />
          <button className="btn btn-primary" onClick={handleGetCep}>
            <MailCheck size={18} className="icon" />
            Confirmar CEP
          </button>
        </div>
      )}

      {address && (
        <>
          {isEditing ? (
              <textarea
                value={address}
                onChange={(e) => {
                  setAddress(e.target.value);
                  e.target.style.height = "auto"; // reset
                  e.target.style.height = `${e.target.scrollHeight}px`; // ajustar
                }}
                className="address-textarea"
                rows={1}
                autoFocus
              />
          ) : (
              <textarea
                ref={textareaRef}
                value={address}
                readOnly={!isEditing}
                onChange={(e) => {
                  setAddress(e.target.value);
                  e.target.style.height = "auto";
                  e.target.style.height = `${e.target.scrollHeight}px`;
                }}
                className="address-textarea"
                rows={1}
                autoFocus={isEditing}
              />
          )}

          <h3>O endereço está correto?</h3>

          <div className="btn-group">
            <button className="btn btn-primary" onClick={onConfirm}>
              <CheckCircle size={20} className="icon" />
              Sim, correto
            </button>
            <button className="btn btn-outline" onClick={onReject}>
              <XCircle size={20} className="icon" />
              Não, voltar
            </button>
            {!isEditing && (
              <button className="btn btn-outline" onClick={handleEditToggle}>
                <Pencil size={20} className="icon" />
                Editar
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ConfirmLocationCard;
