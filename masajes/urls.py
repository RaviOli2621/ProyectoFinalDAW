from django.urls import path
from . import views
urlpatterns = [
    path('masajes/', views.masajes,name="masajes"),
    path('masaje/', views.masaje,name="masaje"),
    path('calendari/', views.calendari,name="calendari"),
    path('reservas/', views.reserves,name="reservas"),
    path('reservar/', views.reservar,name="reservar"),
    path('pago_tarjeta/', views.pago_tarjeta, name='pago_tarjeta'),
    path('confirmacion_pago/', views.masajes, name='confirmacion_pago'),
]
