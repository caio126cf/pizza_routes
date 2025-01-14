from django.shortcuts import render
import pytesseract
from django.http import JsonResponse
from rest_framework.decorators import api_view
import googlemaps
import re

path_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.tesseract_cmd = path_tesseract

# Create your views here.

@api_view(['POST'])
def process_image(request):
    # Salva a imagem enviada
    image = request.FILES['image']

    # Processa OCR diretamente no arquivo
    text = pytesseract.image_to_string(image)

    # Extrai endereços usando regex
    addresses = re.findall(r'\d{5}-\d{3}|\w+\s\d+', text)

    # Ordena os endereços com Google Maps API
    gmaps = googlemaps.Client(key='YOUR_GOOGLE_API_KEY')
    origin = "YOUR_ORIGIN_LAT,LONG"
    destinations = addresses

    # Obtém a matriz de distâncias
    distances = gmaps.distance_matrix(origins=origin, destinations=destinations)
    sorted_addresses = sorted(
        destinations,
        key=lambda addr: distances['rows'][0]['elements'][destinations.index(addr)]['distance']['value']
    )

    # Gera o link do Waze
    waze_url = "https://waze.com/ul?" + "&".join(
        [f"ll={addr}&navigate=yes" for addr in sorted_addresses]
    )

    return JsonResponse({"waze_url": waze_url, "addresses": sorted_addresses})