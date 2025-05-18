import datetime
from .views import correo
from django.utils import timezone  
from usuarios.models import Reserva


def manage_reservations():
    """Tarea principal que ejecuta las subtareas programadas"""
    # Notificar reservas de mañana
    usuarios_mañana = notificar_usuarios_reservas_mañana()
    
    trabajadoresEl = eliminar_trabajadores_vencidos()

    # Eliminar reservas antiguas
    eliminadas = eliminar_reservas_pasadas()
    
    return f"Se notificaron {len(usuarios_mañana)} usuarios con reservas para mañana " \
           f"y se eliminaron {eliminadas} reservas antiguas." \
           f" Trabajadores eliminados: {trabajadoresEl['trabajadores_eliminados']}." 

def notificar_usuarios_reservas_mañana():
    """Notifica a usuarios con reservas programadas para el día siguiente"""
    usuarios = get_usuarios_reservas_mañana()
    
    for usuario, reservas in usuarios.items():
        # Construir el mensaje con detalles de las reservas
        detalles_reservas = "\n".join([
            f"- {reserva.idMasaje.nombre} a las {reserva.fecha.strftime('%H:%M')}" 
            for reserva in reservas
        ])
        
        correo(
            "Recordatorio de reservas para mañana",
            f"Hola {usuario.username},\n\n"
            f"Te recordamos que tienes las siguientes reservas programadas para mañana:\n\n"
            f"{detalles_reservas}\n\n"
            f"¡Te esperamos! Si necesitas cambiar o cancelar tu reserva, "
            f"por favor contáctanos con anticipación.",
            "Recordatorio de reserva",
            "sistema@lmsmasajes.com",
            usuario.email
        )
    
    return usuarios

def eliminar_reservas_pasadas(dias=0):
    # Calcular la fecha límite (por defecto, hoy)
    fecha_limite = timezone.now().date() - timezone.timedelta(days=dias)
    
    # Refactor: usa método del modelo
    eliminadas = Reserva.delete_older_than(fecha_limite)
    
    return eliminadas[0] if eliminadas and isinstance(eliminadas, tuple) else 0

def get_usuarios_reservas_mañana():
    mañana = timezone.now().date() + timezone.timedelta(days=1)
    print(f"Buscando reservas para: {mañana}")
    
    inicio_mañana = timezone.make_aware(datetime.datetime.combine(mañana, datetime.time.min))
    fin_mañana = timezone.make_aware(datetime.datetime.combine(mañana, datetime.time.max))
    
    print(f"Rango de búsqueda: {inicio_mañana} hasta {fin_mañana}")
    
    # Refactor: usa método del modelo
    reservas_mañana = Reserva.get_for_date_range(inicio_mañana, fin_mañana)
    print(f"Reservas encontradas: {reservas_mañana.count()}")
    
    usuarios_reservas = {}
    for reserva in reservas_mañana:
        if reserva.idCliente not in usuarios_reservas:
            usuarios_reservas[reserva.idCliente] = []
        usuarios_reservas[reserva.idCliente].append(reserva)
    
    return usuarios_reservas

def eliminar_trabajadores_vencidos():
    from usuarios.models import Worker
    hoy = timezone.now().date()
    print(f"Buscando trabajadores con fecha de eliminación vencida (hoy es {hoy})")
    resultado = Worker.eliminar_trabajadores_vencidos(fecha=hoy)
    print(f"Proceso completado: {resultado['trabajadores_eliminados']} trabajadores y {resultado['usuarios_eliminados']} usuarios eliminados.")
    return resultado