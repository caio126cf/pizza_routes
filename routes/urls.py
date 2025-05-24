# routes/urls.py
from django.urls import path # type: ignore
from .views import *  # Importa a função view

urlpatterns = [
    path('delivery-route/', delivery_route, name='delivery_route'),
    path('check-address/', check_address, name='check_address'),
    path('image-extract/', image_extract, name='image_extract'),
]