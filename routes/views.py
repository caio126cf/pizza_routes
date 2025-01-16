from django.shortcuts import render
import pytesseract
from django.http import JsonResponse
from rest_framework.decorators import api_view
from PIL import Image
import re

# Caminho para o executável do Tesseract no seu sistema
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Função de view para processar a imagem e retornar endereços via string
@api_view(['POST'])
def process_image(request):
    # Verifica se a imagem foi enviada
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    # Obtém o arquivo de imagem enviado
    image_file = request.FILES['image']
    image = Image.open(image_file)
    extracted_text = pytesseract.image_to_string(image)

    # Substituir múltiplas quebras de linha por um espaço
    cleaned_text = re.sub(r'\n+', ' ', extracted_text)  

    # Regex para capturar os dados entre '#' e 'SP'
    delivery_info = re.findall(r'#\d{5}.*?SP', cleaned_text)

    # Limpar os dados, removendo o padrão '#12345'
    delivery_addresses = [re.sub(r"#\d{5}", "", info) for info in delivery_info]

    # Verifica se encontrou endereços
    if not delivery_addresses:
        return JsonResponse({'error': 'No addresses found in the image'}, status=400)

    # Retorna os endereços encontrados em formato JSON
    return JsonResponse({"addresses": delivery_addresses})
