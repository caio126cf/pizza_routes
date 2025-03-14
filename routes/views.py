from django.http import JsonResponse
from PIL import Image
import pytesseract
import re
import requests
import os
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

def consultar_cep(request):
    if request.method != "POST":
        return api_response("consultar_cep", error="Método não permitido")
    
    print("Consultando CEP...", flush=True)
    cep = request.POST.get('cep')
    
    if not cep or not cep.isdigit() or len(cep) != 8:
        return api_response("consultar_cep", error="CEP inválido")
    
    count_api_call("viacep")
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    data = response.json()
    
    if not data:
        return api_response("consultar_cep", error="VIA Cep API não retornou dados.")
    
    return api_response("consultar_cep", data=data)

def extract_text_from_image(image_file):
    print("Extraindo texto da imagem...", flush=True)
    image = Image.open(image_file)
    
    if image.format not in ["JPEG", "PNG", "BMP", "GIF", "TIFF"]:
        return api_response("extract_text_from_image", error="Formato de imagem inválido.")
    
    extracted_text = pytesseract.image_to_string(image)
    delivery_info = re.findall(r'#\d{5}.*?SP', re.sub(r'\n+', ' ', extracted_text))
    delivery_addresses = [re.sub(r"#\d{5}", "", info).strip() for info in delivery_info]
    
    if not delivery_addresses:
        return api_response("extract_text_from_image", error="Não foi possível extrair endereços da imagem.")
    
    return delivery_addresses

def nearest_neighbor(origin, addresses):
    print("Calculando a rota otimizada...", flush=True)
    if not addresses or not isinstance(addresses, list):
        return api_response("nearest_neighbor", error="Endereços inválidos ou não fornecidos.")
    
    route, current_location, remaining_addresses = [origin], origin, addresses[:]
    
    while remaining_addresses:
        distances = get_distances(current_location, remaining_addresses)
        valid_distances = {addr: dist for addr, dist in distances.items() if dist is not None}
        
        if not valid_distances:
            break
        
        next_address = min(valid_distances, key=valid_distances.get)
        route.append(next_address)
        current_location = next_address
        remaining_addresses.remove(next_address)
    
    return route

def get_distances(origin, destinations):
    print(f"Calculando distâncias a partir de {origin}...", flush=True)
    
    count_api_call("google_distance_matrix")
    response = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={"origins": origin, "destinations": "|".join(destinations), "key": GOOGLE_API_KEY}
    )
    
    if not response.ok:
        return {}
    
    data = response.json()
    
    if "rows" not in data or not data["rows"] or "elements" not in data["rows"][0]:
        return {}
    
    distances = {}
    for i, element in enumerate(data["rows"][0]["elements"]):
        distances[destinations[i]] = element["distance"]["value"] if element.get("status") == "OK" else None
    
    return distances

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
def process_request(request):
    if request.method != "POST":
        return api_response("process_request", error="Método não permitido")
    
    print("Processando a requisição...", flush=True)
    
    if 'image' not in request.FILES:
        return api_response("process_request", error="Imagem não recebida via request.")
    
    user_location = request.POST.get('current_location')
    cep = request.POST.get('cep')
    
    if cep and not user_location:
        user_location = get_coordinates_from_address(cep)
        if not user_location:
            return api_response("process_request", error="CEP inválido.")
    
    delivery_addresses = extract_text_from_image(request.FILES['image'])
    if not delivery_addresses:
        return api_response("process_request", error="Extração do texto da imagem falhou.")

    optimized_route = nearest_neighbor(user_location, delivery_addresses)
    google_maps_url = generate_google_maps_url(optimized_route)
    return api_response("process_request", data={
        "optimized_route": optimized_route,
        "google_maps_url": google_maps_url
    })
    
# BACKEND ESTA FUNCIONANDO PASSANDO O CEP NO FORMATO CEP
# OU USER_LOCATION NO FORMATO QUE O NAVEGADOR CAPTURA (LATITUDE E LONGITUDE)
# AGORA, FAZER A PARTE DO FRONTEND. DECIDIR COMO FARA A DIVISAO DE CAPTURA DE LOCALZIACAO OU CEP
