from django.http import JsonResponse
from rest_framework.decorators import api_view
from PIL import Image
import pytesseract
import re
import requests
import os
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import status

load_dotenv()
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@api_view(['POST'])
def consultar_cep(request):
    print("Consultando CEP...")
    cep = request.data.get('cep')
    
    if not cep or len(cep) != 8:
        return Response({'error': 'CEP inválido'}, status=status.HTTP_400_BAD_REQUEST)
    
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    data = response.json()

    if 'erro' in data:
        return Response({'error': 'CEP não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def process_image(request):
    print("Processando imagem...")
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)
    
    user_location = request.query_params.get('current_location')
    manual_address = request.query_params.get('manual_address')

    if not user_location and not manual_address:
        return JsonResponse({'error': 'No location or address provided'}, status=400)

    if manual_address:
        if len(manual_address) == 8 and manual_address.isdigit():
            user_location = get_coordinates_from_address(manual_address)
            if not user_location:
                return JsonResponse({'error': 'Invalid manual address (CEP)'}, status=400)
        else:
            user_location = get_coordinates_from_address(manual_address)
            if not user_location:
                return JsonResponse({'error': 'Invalid manual address'}, status=400)
    else:
        latitude, longitude = user_location.split(',')
        user_location = f"{latitude},{longitude}"

    image = Image.open(request.FILES['image'])
    if image.format not in ["JPEG", "PNG", "BMP", "GIF", "TIFF"]:
        return JsonResponse({'error': 'Unsupported image format'}, status=400)
    
    extracted_text = pytesseract.image_to_string(image)
    delivery_info = re.findall(r'#\d{5}.*?SP', re.sub(r'\n+', ' ', extracted_text))
    delivery_addresses = [re.sub(r"#\d{5}", "", info).strip() for info in delivery_info]

    if not delivery_addresses:
        return JsonResponse({'error': 'No valid addresses found in the image'}, status=400)
    
    optimized_route = nearest_neighbor(user_location, delivery_addresses)
    google_maps_url = generate_google_maps_url(optimized_route)

    return JsonResponse({"optimized_route": optimized_route, "google_maps_url": google_maps_url})

def nearest_neighbor(origin, addresses):
    print("Calculando a rota otimizada...")
    if not addresses:
        return [origin]
    
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
    
    return route

def get_distances(origin, destinations):
    print(f"Calculando distâncias a partir de {origin}...")
    response = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={"origins": origin, "destinations": "|".join(destinations), "key": GOOGLE_API_KEY}
    )
    
    data, distances = response.json(), {}
    if 'rows' in data and data['rows'] and 'elements' in data['rows'][0]:
        for i, element in enumerate(data['rows'][0]['elements']):
            if element['status'] == "OK":
                distances[destinations[i]] = element['distance']['value']
    
    return distances

def generate_google_maps_url(route):
    print("Gerando URL para o Google Maps...")
    google_maps_url = "https://www.google.com/maps/dir/?api=1"
    google_maps_url += f"&origin={route[0]}"
    google_maps_url += "&destination=" + route[-1]
    
    if len(route) > 2:
        google_maps_url += "&waypoints=" + "|".join(route[1:-1])
    
    return google_maps_url

def get_coordinates_from_address(address):
    print(f"Obtendo coordenadas para o endereço: {address}...")
    response = requests.get(f"https://viacep.com.br/ws/{address}/json/")
    data = response.json()
    
    if 'erro' in data:
        return None
    
    full_address = f"{data['logradouro']}, {data['bairro']}, {data['localidade']} - {data['uf']}"
    geo_response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={full_address}&key={GOOGLE_API_KEY}")
    
    geo_data = geo_response.json()
    if 'results' in geo_data and geo_data['results']:
        lat_lng = geo_data['results'][0]['geometry']['location']
        return f"{lat_lng['lat']},{lat_lng['lng']}"
    
    return None

# REVISAR TODO O BACKEND AFIM DE ENTENDER TODA A LOGICA, RETIRAR MENSAGENS DE ERROS DESNECESSARIAS.
# O ERRO PARECE ESTAR NA GET_COORDINATES_FROM_ADDRESS, POIS O ERRO ESTA NO RETORNO DESSA FUNÇÃO.
# REVISAR O FRONTEND TAMBÉM, POIS PODE HAVER ERROS DE IMPLEMENTAÇÃO.
# RETIRAR DEPENDENCIAS NAO UTILIZADAS.
