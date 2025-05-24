from django.http import JsonResponse
from PIL import Image
import pytesseract
import re
import requests
import os
import json
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def api_response(function, data=None, error=""):
    return JsonResponse({
        "function": function,
        "data": data,
        "error": error
    })
    
api_call_counter = {}

def count_api_call(api_name):
    """Função para contar chamadas de uma API específica."""
    api_call_counter[api_name] = api_call_counter.get(api_name, 0) + 1
    print(f"API '{api_name}' chamada {api_call_counter[api_name]} vezes.")

def check_address(request):
    if request.method != "POST":
        return api_response("check_address", error="Método não permitido")
    
    print("Consultando CEP...", flush=True)
    cep = request.POST.get('cep')
    
    if not cep or not cep.isdigit() or len(cep) != 8:
        return api_response("check_address", error="CEP inválido")
    
    count_api_call("viacep")
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    data = response.json()
    
    if not data:
        return api_response("check_address", error="VIA Cep API não retornou dados.")
    
    return api_response("check_address", data=data)

@csrf_exempt
def image_extract(request):
    if request.method != "POST":
        return api_response("image_extract", error="Método não permitido")
    
    if 'image' not in request.FILES:
        return api_response("delivery_route", error="Imagem não recebida via request.")

    image = Image.open(request.FILES['image'])

    if image.format not in ["JPEG", "PNG", "BMP", "GIF", "TIFF"]:
        return api_response("image_extract", error="Formato de imagem inválido.")
    
    extracted_text = pytesseract.image_to_string(image)
    delivery_info = re.findall(r'#\d{5}.*?SP', re.sub(r'\n+', ' ', extracted_text))
    delivery_addresses = [re.sub(r"#\d{5}", "", info).strip() for info in delivery_info]

    if not delivery_addresses:
        return api_response("image_extract", error="Não foi possível extrair endereços da imagem.")
    
    return api_response("image_extract", data=delivery_addresses)

def nearest_neighbor(origin, addresses):
    print("[nearest_neighbor] Iniciando cálculo da rota otimizada...", flush=True)
    print(f"[nearest_neighbor] Origem: {origin} | Endereços: {addresses}", flush=True)

    if not addresses or not isinstance(addresses, list):
        print("[nearest_neighbor] Endereços inválidos ou não fornecidos.", flush=True)
        return api_response("nearest_neighbor", error="Endereços inválidos ou não fornecidos.")

    route = [origin]
    current_location = origin
    remaining_addresses = addresses[:]

    while remaining_addresses:
        print(f"[nearest_neighbor] Calculando distâncias de {current_location} para {remaining_addresses}", flush=True)
        count_api_call("google_distance_matrix")
        response = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={"origins": current_location, "destinations": "|".join(remaining_addresses), "key": GOOGLE_API_KEY}
        )
        if not response.ok:
            print(">>>>>>>>> Erro ao consultar API do Google.", flush=True)
            return api_response("nearest_neighbor", error="Erro ao consultar API do Google.")

        data = response.json()
        if "rows" not in data or not data["rows"] or "elements" not in data["rows"][0]:
            break

        distances = {}
        for i, element in enumerate(data["rows"][0]["elements"]):
            if element.get("status") == "OK":
                distances[remaining_addresses[i]] = element["distance"]["value"]
            else:
                distances[remaining_addresses[i]] = None

        # Seleciona o próximo endereço mais próximo
        min_distance = None
        next_address = None
        for addr in remaining_addresses:
            dist = distances.get(addr)
            if dist is not None and (min_distance is None or dist < min_distance):
                min_distance = dist
                next_address = addr

        if next_address is None:
            break

        route.append(next_address)
        current_location = next_address
        remaining_addresses.remove(next_address)

    print(f"[nearest_neighbor] Rota final otimizada: {route}", flush=True)
    return route

def generate_google_maps_url(route):
    print("Gerando URL para o Google Maps...", flush=True)
    google_maps_url = "https://www.google.com/maps/dir/?api=1"
    google_maps_url += f"&origin={route[0]}"
    google_maps_url += "&destination=" + route[-1]
    
    if len(route) > 2:
        google_maps_url += "&waypoints=" + "|".join(route[1:-1])
    print(f"URL gerada: {google_maps_url}")
    return google_maps_url

def get_coordinates_from_address(address):
    print(f"Obtendo coordenadas para o endereço: {address}...", flush=True)
    
    count_api_call("google_geocode")
    response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json", params={"address": address, "key": GOOGLE_API_KEY})
    
    if not response.ok:
        return None
    
    geo_data = response.json()
    if "results" in geo_data and geo_data["results"]:
        lat_lng = geo_data["results"][0]["geometry"]["location"]
        return f"{lat_lng['lat']},{lat_lng['lng']}"
    
    return None

@csrf_exempt # type: ignore
def delivery_route(request):
    if request.method != "POST":
        return api_response("delivery_route", error="Método não permitido")
    
    user_location = request.POST.get('user_location')
    delivery_addresses = request.POST.get('delivery_addresses')
    
    delivery_addresses_list = json.loads(delivery_addresses)

    if delivery_addresses_list:
        optimized_route = nearest_neighbor(user_location, delivery_addresses_list)
        google_maps_url = generate_google_maps_url(optimized_route)
        return api_response("delivery_route", data={
            "optimized_route": optimized_route,
            "google_maps_url": google_maps_url
        })
    else:
        return api_response("delivery_route", error="Formato inválido para 'delivery_addresses'.")

    
