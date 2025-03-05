# routes/urls.py
from django.urls import path
from .views import *  # Importa a função view

urlpatterns = [
    path('process-image/', process_image, name='process_image'),
    path('consultar-cep/', consultar_cep, name='consultar_cep')
]