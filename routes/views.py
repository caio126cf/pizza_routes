from django.http import JsonResponse
from rest_framework.decorators import api_view
from PIL import Image
import pytesseract
import re
import requests
import os
from dotenv import load_dotenv
from rest_framework.response import Response

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def api_response(function, data=None, error=""):
    response_data = {
        "function": function,
        "data": data,
        "error": error
    }
    return Response(response_data)

@api_view(['POST'])
def consultar_cep(request):
    print("Consultando CEP...", flush=True)
    cep = request.data.get('cep')
    fct= "consultar_cep"
    
    if not cep or not cep.isdigit() or len(cep) != 8:
        return api_response(fct, error="CEP inválido")	
    else:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        data = response.json()
        
        if not data:
            return api_response(fct, error="VIA Cep API não retornou dados.")

        return api_response(fct, data=data)

def extract_text_from_image(image_file):
    print("Extraindo texto da imagem...", flush=True)
    image = Image.open(image_file)
    fct = "extract_text_from_image"
    
    if image.format not in ["JPEG", "PNG", "BMP", "GIF", "TIFF"]:
        return api_response(fct, error="Formato de imagem inválido.")
    
    extracted_text = pytesseract.image_to_string(image)
    delivery_info = re.findall(r'#\d{5}.*?SP', re.sub(r'\n+', ' ', extracted_text))
    delivery_addresses = [re.sub(r"#\d{5}", "", info).strip() for info in delivery_info]
    
    if not delivery_addresses:
        return api_response(fct, error="Não foi possível extrair endereços da imagem.")

    return api_response(fct, data=delivery_addresses)

def nearest_neighbor(origin, addresses):
    print("Calculando a rota otimizada...", flush=True)
    if not addresses or not isinstance(addresses, list):
        return api_response("nearest_neighbor", error="Endereços inválidos ou não fornecidos.")
    
    route, current_location, remaining_addresses = [origin], origin, addresses[:]
    
    while remaining_addresses:
        distances = get_distances(current_location, remaining_addresses)
        valid_distances = {addr: dist for addr, dist in distances.items() if dist != float("inf")}
        
        if not valid_distances:
            break
        
        next_address = min(valid_distances, key=valid_distances.get)
        route.append(next_address)
        current_location = next_address
        remaining_addresses.remove(next_address)
    
    return api_response("nearest_neighbor", data=route)

def get_distances(origin, destinations):
    print(f"Calculando distâncias a partir de {origin}...", flush=True)
    fct= "get_distances"
    
    response = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={"origins": origin, "destinations": "|".join(destinations), "key": GOOGLE_API_KEY}
    )

    if not response:
        return api_response(fct, error="Erro ao consultar o Google Distance Matrix API")

    data = response.json()

    if "rows" not in data or not data["rows"] or "elements" not in data["rows"][0]:
        return api_response(fct, error="Dados inválidos retornados pelo Google Distance Matrix API")

    distances = {}
    for i, element in enumerate(data["rows"][0]["elements"]):
        if element.get("status") == "OK":
            distances[destinations[i]] = element["distance"]["value"]
        else:
            distances[destinations[i]] = None

    return api_response(fct, data=distances)

def generate_google_maps_url(route):
    print("Gerando URL para o Google Maps...", flush=True)
    fct= "generate_google_maps_url"
    print("ROUTE " + str(route), flush=True)
    #google_maps_url = "https://www.google.com/maps/dir/?api=1"
    #google_maps_url += f"&origin={route[0]}"
    #google_maps_url += "&destination=" + route[-1]
    
    #if len(route) > 2:
    #    google_maps_url += "&waypoints=" + "|".join(route[1:-1])
    
    #return api_response(fct, data=google_maps_url)

def get_coordinates_from_address(address):
    print(f"Obtendo coordenadas para o endereço: {address}...", flush=True)
    fct = "get_coordinates_from_address"
    
    response = requests.get(f"https://viacep.com.br/ws/{address}/json/")
    if not response:
        return api_response(fct, error="VIA Ceo não retornou response.")

    data = response.json()
    if not all(k in data for k in ["logradouro", "bairro", "localidade", "uf"]):
        return api_response(fct, error="Informações incompletas no VIACEP")

    full_address = f"{data['logradouro']}, {data['bairro']}, {data['localidade']} - {data['uf']}"
    
    geo_response = requests.get(
        f"https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": full_address, "key": GOOGLE_API_KEY}
    )
    
    if not geo_response:
        return api_response(fct, error="GEOCODE API não retornou response.")

    geo_data = geo_response.json()
    
    if "results" in geo_data and geo_data["results"]:
        lat_lng = geo_data["results"][0]["geometry"]["location"]
        lat_lng_formated = f"{lat_lng['lat']},{lat_lng['lng']}"
        return api_response(fct , data=lat_lng_formated)

    return None 

@api_view(['POST'])
def process_request(request):
    print("Processando a requisição...", flush=True)
    fct = "process_request"
    if 'image' not in request.FILES:
        return api_response(fct, error= 'Imagem não recebida via request.')
    
    user_location = request.data.get('current_location')
    manual_address = request.data.get('manual_address')
    
    if manual_address and not user_location:
        user_location = get_coordinates_from_address(manual_address)
        if not user_location:
            return api_response(fct, error= "Invalid manual address (CEP)")
        
    elif user_location and not manual_address:
        latitude, longitude = user_location.split(',')
        user_location = f"{latitude},{longitude}"
    
    delivery_addresses = extract_text_from_image(request.FILES['image'])
    if not delivery_addresses:
        return  api_response(fct, error= "Extração do texto da imagem não funcionou.")
    
    optimized_route = nearest_neighbor(user_location, delivery_addresses)
    google_maps_url = generate_google_maps_url(optimized_route)
    
    return api_response(fct, data={
        "optimized_route": optimized_route,
        "google_maps_url": google_maps_url
        })
    
# DEBUGAR BACKEND, QUANDO ESTIVER FUNCIONANDO, AJUSTAR FRONTEND.
# FAÇA PASSO A PASSO A PARTIR DA PROCESS_REQUEST
