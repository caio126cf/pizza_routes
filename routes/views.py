from django.shortcuts import render
import pytesseract
from django.http import JsonResponse
from rest_framework.decorators import api_view
from PIL import Image
import re

# Caminho para o executável do Tesseract no seu sistema
path_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.tesseract_cmd = path_tesseract

# Função de view para processar a imagem e retornar endereços via string
@api_view(['POST'])
def process_image(request):
    # Verifica se a imagem foi enviada
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    # Obtém o arquivo de imagem enviado
    image_file = request.FILES['image']

    # Tenta abrir a imagem e realizar OCR
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        return JsonResponse({'error': f'Error processing image: {str(e)}'}, status=500)

    # Extrai endereços usando expressão regular
    addresses = re.findall(r'\d{5}-\d{3}|\w+\s\d+', text)

    # Verifica se encontrou endereços
    if not addresses:
        return JsonResponse({'error': 'No addresses found in the image'}, status=400)

    # Retorna os endereços encontrados
    return JsonResponse({"addresses": addresses})
