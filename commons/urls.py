from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('enviar-correo/', views.enviar_correo, name='enviar_correo'),

]
