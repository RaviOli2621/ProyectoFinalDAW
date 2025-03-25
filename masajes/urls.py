from django.urls import path
from . import views
urlpatterns = [
    path('masajes/', views.masajes,name="masajes")
]
