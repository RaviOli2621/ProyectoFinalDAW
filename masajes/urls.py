from django.urls import path
from . import views
urlpatterns = [
    path('masajes/', views.masajes,name="masajes"),
    path('masaje/', views.masaje,name="masaje"),
    path('calendari/', views.calendari,name="calendari"),
    path('reservas/', views.reserves,name="reservas"),
    path('reservar/', views.reserves,name="reservar")
]
