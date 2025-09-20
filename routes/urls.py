# # routes/urls.py
# from django.urls import path # type: ignore
# from .views import *  # Importa a função view

# urlpatterns = [
#     path('delivery-route/', delivery_route, name='delivery_route'),
#     path('check-address/', check_address, name='check_address'),
#     path('image-extract/', image_extract, name='image_extract'),
# ]

from django.urls import path
from .views import *

urlpatterns = [
    path('check-address/', CheckAddressView.as_view(), name='check_address'),
    path('image-extract/', ImageExtractView.as_view(), name='image_extract'),
    path('delivery-route/', DeliveryRouteView.as_view(), name='delivery_route'),
    path('test-auth/', TestAuthView.as_view(), name='test-auth')
]
