import React, { useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';

const Container = styled.div`
  font-family: 'Arial', sans-serif;
  padding: 20px;
  max-width: 800px;
  margin: auto;
  background-color: #f4f7fc;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
`;

const Header = styled.h1`
  font-size: 2rem;
  text-align: center;
  color: #4A90E2;
`;

const Button = styled.button`
  background-color: #4A90E2;
  color: white;
  font-size: 1rem;
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #357ABD;
  }

  &:disabled {
    background-color: #D1D8E0;
    cursor: not-allowed;
  }
`;

const Input = styled.input`
  display: block;
  width: 100%;
  padding: 12px;
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
`;

const LocationText = styled.p`
  font-size: 1rem;
  color: #4A90E2;
  text-align: center;
`;

const RouteList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const RouteItem = styled.li`
  font-size: 1rem;
  padding: 10px 0;
  border-bottom: 1px solid #ddd;
`;

const ErrorText = styled.p`
  text-align: center;
  color: red;
`;

const App = () => {
  const [image, setImage] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [manualAddress, setManualAddress] = useState('');
  const [cepData, setCepData] = useState(null);
  const [optimizedRoute, setOptimizedRoute] = useState([]);
  const [googleMapsUrl, setGoogleMapsUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation(`${position.coords.latitude},${position.coords.longitude}`);
        },
        (error) => {
          setError("Erro ao obter localização");
        }
      );
    } else {
      setError("Geolocalização não suportada");
    }
  };

  const handleCepChange = (e) => {
    const cep = e.target.value;
    setManualAddress(cep);
  };

  const handleFetchCep = async () => {
    if (manualAddress.length === 8) {
      try {
        const response = await axios.post('http://localhost:8000/api/consultar-cep/', {
          cep: manualAddress
        });
        if (response.data) {
          setCepData(response.data);
          setError(null);
        } else {
          setError("CEP não encontrado");
        }
      } catch (err) {
        setError("Erro ao buscar o CEP");
      }
    } else {
      setError("Digite um CEP válido");
    }
  };

  const handleImageUpload = async () => {
    if (!image || (!currentLocation && !manualAddress && !cepData)) {
      setError('Por favor, forneça uma imagem e sua localização ou endereço');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);

    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/process-image/', formData, {
        params: {
          current_location: currentLocation,
          manual_address: manualAddress || `${cepData?.logradouro}, ${cepData?.bairro}, ${cepData?.localidade} - ${cepData?.uf}`
        },
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setOptimizedRoute(response.data.optimized_route);
      setGoogleMapsUrl(response.data.google_maps_url);
      setLoading(false);
    } catch (err) {
      setError("Erro ao processar a imagem. Tente novamente.");
      setLoading(false);
    }
  };

  return (
    <Container>
      <Header>Envie a Imagem para Processar a Rota</Header>
      
      <Button onClick={getCurrentLocation}>Obter Localização Atual</Button>
      {currentLocation && <LocationText>Localização atual: {currentLocation}</LocationText>}

      <Input
        type="text"
        placeholder="Digite o CEP"
        value={manualAddress}
        onChange={handleCepChange}
      />
      
      <Button onClick={handleFetchCep} disabled={loading}>
        {loading ? "Buscando..." : "Buscar Endereço"}
      </Button>

      {cepData && (
        <div>
          <p>Endereço encontrado:</p>
          <p>{cepData.logradouro}, {cepData.bairro}, {cepData.localidade} - {cepData.uf}</p>
        </div>
      )}

      <Input
        type="file"
        accept="image/*"
        onChange={(e) => setImage(e.target.files[0])}
      />
      
      <Button onClick={handleImageUpload} disabled={loading}>
        {loading ? "Processando..." : "Processar Imagem"}
      </Button>

      {optimizedRoute.length > 0 && (
        <div>
          <h3>Rota Otimizada</h3>
          <RouteList>
            {optimizedRoute.map((address, index) => (
              <RouteItem key={index}>{address}</RouteItem>
            ))}
          </RouteList>
        </div>
      )}

      {googleMapsUrl && (
        <div>
          <h3>Veja a Rota no Google Maps</h3>
          <a href={googleMapsUrl} target="_blank" rel="noopener noreferrer">
            <Button>Ir para a entrega</Button>
          </a>
        </div>
      )}

      {error && <ErrorText>{error}</ErrorText>}
    </Container>
  );
};

export default App;
