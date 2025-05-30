from django.urls import path
from . import views
urlpatterns = [
    path('masajes/', views.masajes,name="masajes"),
    path('masaje/', views.masaje,name="masaje"),
    path('reservas/', views.reserves,name="reservas"),
    path('reservar/', views.reservar,name="reservar"),

    path('worker_ver_masaje/', views.workerReserves,name="woker_reservas"),
    path('get_reserva_by_id/', views.getReservaById,name="get_reserva_by_id"),

    path('pago_tarjeta/', views.pago_tarjeta, name='pago_tarjeta'),
    path('reservar_cambio/', views.editar_reserva,name="reservar_cambio"),
    path('pago_tarjeta_cambio/', views.editar_pago_tarjeta, name='pago_tarjeta_cambio'),
    path('confirmacion_pago/', views.masajes, name='confirmacion_pago'),
    path('borrar_reserva/<int:reserva_id>/', views.borrar_reserva, name='borrar_reserva'),  

    path('api/calendario/', views.calendario_api, name='calendario_api'),
    path('api/horas/', views.horas_api, name='horas_api'),

    path('calendari/', views.calendari,name="calendari"),
    path('api/calendari/fiestas/', views.gestionarDiasFiesta,name="calendari_fiestas"),
    path('api/calendari/fiestas/trabajador/', views.fiestaTrabajador,name="trabajador_fiestas"),
    path('api/calendari/fiestas/trabajador/<int:idTrabajador>/', views.cambiarFiestatrabajador,name="trabajador_fiestas"),
]
