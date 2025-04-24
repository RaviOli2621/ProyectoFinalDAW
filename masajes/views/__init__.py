# Import functions from views.masaje
from .masaje import (
    notAdmin_user,
    safe_aware,
    masajes,
    masaje
)

# Import functions from views.reserva
from .reserva import (
    reserves,
    reservar,
    pago_tarjeta,
    editar_reserva,
    editar_pago_tarjeta,
    borrar_reserva
)

# Import functions from views.calendar
from .calendar import (
    calendari,
    calcDiaCalendario,
    calendario_api,
    horas_api,
    gestionarDiasFiesta,
    fiestaTrabajador
)

# Make all functions available at the package level
__all__ = [
    'notAdmin_user',
    'safe_aware',
    'masajes',
    'masaje',
    'reserves',
    'reservar',
    'pago_tarjeta',
    'editar_reserva',
    'editar_pago_tarjeta',
    'borrar_reserva',
    'calendari',
    'calcDiaCalendario',
    'calendario_api',
    'horas_api'
]
