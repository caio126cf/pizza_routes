# routes/urls.py
from django.urls import path
from .views import *  # Importa a função view

urlpatterns = [
    path('process_request/', process_request, name='process_request'),
    path('consultar-cep/', consultar_cep, name='consultar_cep')
]