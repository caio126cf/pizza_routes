# routes/urls.py
from django.urls import path
from .views import process_image  # Importa a função view

urlpatterns = [
    path('process-image/', process_image, name='process_image'),  # Define a rota para a API
]