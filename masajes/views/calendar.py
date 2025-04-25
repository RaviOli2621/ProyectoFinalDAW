from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.forms import ReservaForm, TarjetaForm
from usuarios.models import Fiestas, Reserva, Worker
from masajes.models import Masaje, TipoMasaje
from commons.utils import get_filename  # Importamos la función de utilidad
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Import User model
from django.utils.timezone import make_aware, is_naive
from django.views.decorators.http import require_http_methods
from django.db.models import F, ExpressionWrapper, DateTimeField, DurationField

def notAdmin_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return wrapper_func
# ApiS para el calendario
def safe_aware(dt):
    if is_naive(dt):
        return make_aware(dt)
    return dt
def calcDiaCalendario(dia_evento, current_date, workers, delta,blue,duracion):
    if current_date <= datetime.now().date():
        dia_evento["backgroundColor"] = "red"
        return dia_evento

    if current_date.weekday() in {5, 6}:
        dia_evento["color"] = "gray"
        return dia_evento
    if Fiestas.objects.filter(fecha=current_date, general=True).exists():
        if blue==True: dia_evento["color"] = "blue" 
        else: dia_evento["color"] = "gray"
        return dia_evento

    franjas = [
        safe_aware(datetime.combine(current_date, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    franjas = quitarHorasDeDescanso(franjas)

    horas_ocupadas = 0
    ocupacionGeneral = 0
    for franja_inicio in franjas:
        duracionFormated = 30  # Default value
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
            # If it's a numeric string
                duracionFormated = int(duracion)
            else:
            # Try to parse as time format "HH:MM:SS"
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        duracionFormated = 30  # Default value
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
            # If it's a numeric string
                duracionFormated = int(duracion)
            else:
            # Try to parse as time format "HH:MM:SS"
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        # Trabajadores disponibles en la franja
        workersThisHour = workers.filter(
            start_time__lt=franja_fin.time(),
            end_time__gt=franja_inicio.time()
        )
        total_workers = workersThisHour.count()

        # Festivos personales SOLO de los que trabajan en esta franja
        festivos_personales = Fiestas.objects.filter(
            fecha=current_date,
            general=False,
            empleado_id__in=workersThisHour.values_list('id', flat=True)
        ).count()

        workers_disponibles = total_workers - festivos_personales

        reservas = Reserva.objects.filter(
            fecha__lte=franja_inicio,
        )

        ocupacion = 0
        for r in reservas:
            inicio = r.fecha
            duracio = r.duracion or r.idMasaje.duracion
            fin = inicio + duracio
            if inicio < franja_fin and fin > franja_inicio:
                ocupacion += 1

        if ocupacion >= workers_disponibles:
            horas_ocupadas += 1
        ocupacionGeneral += ocupacion
    # Clasificar el día según ocupación
    if horas_ocupadas == 0 and ocupacionGeneral == 0:
        dia_evento["backgroundColor"] = "green"
    elif horas_ocupadas >= len(franjas):
        dia_evento["backgroundColor"] = "red"
    else:
        dia_evento["backgroundColor"] = "orange"
    return dia_evento
def calendario_api(request):
    eventos = []
    # Obtener año y mes del request, o usar los actuales por defecto
    year = int(request.GET.get('year', request.GET['year']))
    month = int(request.GET.get('month', request.GET['month']))
    blue = request.GET.get('blue', request.GET.get('blue', True))
    duradacion = request.GET.get('duracion', request.GET.get('duracion', 30))
    # Calcular rango de días a mostrar (incluyendo días del mes anterior/siguiente)
    start_date = datetime(year, month, 1).date()
    end_date = (start_date.replace(day=28) + timedelta(days=10)).replace(day=1)
    delta = timedelta(days=1)

    # Obtener información de trabajadores
    workers = Worker.objects.filter(delete_date__isnull=True)

    current_date = start_date
    while current_date < end_date:
        dia_evento = {"start": current_date.isoformat(), "display": "background"}
       
        dia_evento = calcDiaCalendario(dia_evento, current_date, workers, delta,blue,duradacion)

        eventos.append(dia_evento)
        current_date += delta

    return JsonResponse(eventos, safe=False)
def horas_api(request):
    # Obtener el día seleccionado del calendario
    fecha_seleccionada = request.GET.get('fecha')
    duracion = request.GET.get('duracion')
    fecha = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()

    # Crear un diccionario para almacenar las horas ocupadas
    horas_ocupadas = []

    franjas = [
    safe_aware(datetime.combine(fecha, time(8, 0)) + timedelta(minutes=30 * i))
    for i in range(28)
    ]
    workers = Worker.objects.filter(delete_date__isnull=True)
    franjas = quitarHorasDeDescanso(franjas)
    for franja_inicio in franjas:
        # Process duration value based on its type
        duracionFormated = 30  # Default value
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
            # If it's a numeric string
                duracionFormated = int(duracion)
            else:
            # Try to parse as time format "HH:MM:SS"
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        reservas = Reserva.objects.filter(
            fecha__lte=franja_inicio,
            fecha__gte=franja_inicio - timedelta(hours=3)  # margen para masajes largos
        )
        workersThisHour = workers.filter(
            start_time__lt=franja_fin.time(),
            end_time__gt=franja_inicio.time()
        )
        total_workers = workersThisHour.count()
        horas_disponibles = total_workers

        for r in reservas:
            inicio = r.fecha  
            duracion = r.duracion if r.duracion else r.idMasaje.duracion
            fin = inicio + duracion

            if inicio < franja_fin and fin > franja_inicio:
                horas_disponibles -= 1
             
        if horas_disponibles <= 0:
            print(f"franja: {franja_inicio} trabajadores: {total_workers} {reservas}")
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"red"})
        elif horas_disponibles < workersThisHour.count():
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"orange"})
        else:
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"green"})
    return JsonResponse(horas_ocupadas, safe=False)
def quitarHorasDeDescanso(franjas):
    franjas = [franja for franja in franjas if franja.time() not in {time(13, 0),time(13, 30), time(19, 0),time(19, 30)}]
    return franjas

@require_http_methods(["PUT", "DELETE"])
def gestionarDiasFiesta(request):
    dia = request.GET.get('fecha')

    if request.method == "PUT":
        # Handle the PUT method
        reservas = Reserva.objects.filter(fecha__date=dia)
        for reserva in reservas:
            # Enviar correo a los usuarios con reservas
            from commons.services.email_service import send_email  # Importar el servicio de correo
            try:
                send_email(
                to_emails=reserva.idCliente.email,
                subject="Cancelación de reserva",
                message=f"Estimado/a {reserva.idCliente.first_name},\n\n"
                    f"Lamentamos informarle que su reserva para el día {dia} ha sido cancelada. Su pago sera reenvolsado de inmediato \n\n"
                    f"Saludos cordiales,\nEl equipo de Masajes."
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                return JsonResponse({"status": "error", "message": "Error sending email to " + reserva.idCliente.email}, status=500)
        reservas.delete()
        Fiestas.objects.create(fecha=dia, general=True)
    elif request.method == "DELETE":
        # Handle the DELETE method
        Fiestas.objects.filter(fecha=dia).delete()
    return JsonResponse({"status": "success"}, status=200)
@notAdmin_user
def calendari(request):
    return render(request,"calendario.html")

def fiestaTrabajador(request):
    eventos = []
    # Obtener año y mes del request, o usar los actuales por defecto
    year = int(request.GET.get('year', request.GET['year']))
    month = int(request.GET.get('month', request.GET['month']))

    # Calcular rango de días a mostrar (incluyendo días del mes anterior/siguiente)
    start_date = datetime(year, month, 1).date()
    end_date = (start_date.replace(day=28) + timedelta(days=10)).replace(day=1)
    delta = timedelta(days=1)

    # Obtener información de trabajadores
    workers = Worker.objects.filter(delete_date__isnull=True)

    worker = Worker.objects.filter(id=request.GET.get('idTrabajador')).first()
    current_date = start_date
    while current_date < end_date:
        dia_evento = {"start": current_date.isoformat(), "display": "background"}
    
        dia_evento = calcFiestaTrabajador(dia_evento, current_date, workers, delta,worker)

        eventos.append(dia_evento)
        current_date += delta

    return JsonResponse(eventos, safe=False)
def calcFiestaTrabajador(dia_evento, current_date, workers, delta, worker):
    # Comprobar si es fiesta específica del trabajador
    duracion = 30
    if worker is not None:
        worker_instance = worker
        if Fiestas.objects.filter(fecha=current_date, general=False, empleado_id=worker_instance.id).exists():
            dia_evento["backgroundColor"] = "blue"
            return dia_evento

    if current_date <= datetime.now().date():
        dia_evento["backgroundColor"] = "red"
        return dia_evento

    if current_date.weekday() in {5, 6} or Fiestas.objects.filter(fecha=current_date, general=True).exists():
        dia_evento["color"] = "gray"
        return dia_evento

    # Comprobar si quitando al worker hay más reservas que trabajadores en alguna franja
    franjas = [
        safe_aware(datetime.combine(current_date, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    franjas = quitarHorasDeDescanso(franjas)

    for franja_inicio in franjas:
        duracionFormated = 30  # Default value
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
            # If it's a numeric string
                duracionFormated = int(duracion)
            else:
            # Try to parse as time format "HH:MM:SS"
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        # Trabajadores disponibles en esa franja, quitando al worker
        workersThisHour = workers.exclude(id=worker.id).filter(
            start_time__lt=franja_fin.time(),
            end_time__gt=franja_inicio.time()
        )
        total_workers = workersThisHour.count()
        reservas = Reserva.objects.filter(
            fecha__lte=franja_inicio,
            fecha__gte=franja_inicio - timedelta(hours=3)
        )

        ocupacion = 0
        for r in reservas:
            inicio = r.fecha
            duracion = r.duracion or r.idMasaje.duracion
            fin = inicio + duracion
            if inicio < franja_fin and fin > franja_inicio:
                ocupacion += 1
        if ocupacion > total_workers:
            dia_evento["backgroundColor"] = "red"
            return dia_evento
    dia_evento["backgroundColor"] = "green"
    return dia_evento

def cambiarFiestatrabajador(request,idTrabajador):
    fecha = request.GET.get('fecha')
    worker = Worker.objects.filter(id=idTrabajador).first()
    fiesta = Fiestas.objects.filter(fecha=fecha, empleado=worker).first()

    workerHoraInicio = worker.start_time
    workerHoraFin = worker.end_time

    if fiesta:
        fiesta.delete()
        return JsonResponse({"status": "success"}, status=200)
    else:
        # Calcular el inicio y fin del horario del trabajador para ese día
        hora_inicio = datetime.combine(datetime.strptime(fecha, "%Y-%m-%d"), workerHoraInicio)
        hora_fin = datetime.combine(datetime.strptime(fecha, "%Y-%m-%d"), workerHoraFin)

        # Filtrar reservas que se solapan con el horario del trabajador
        reserva = Reserva.objects.annotate(
            fin_reserva=ExpressionWrapper(
                F('fecha') + F('duracion'),
                output_field=DateTimeField()
            )
        ).filter(
            fecha__date=fecha,
            fecha__lt=hora_fin,
            fin_reserva__gt=hora_inicio
        ).last()
            # Enviar correo a los usuarios con reservas
        from commons.services.email_service import send_email  # Importar el servicio de correo
        try:
            send_email(
            to_emails=reserva.idCliente.email,
            subject="Cancelación de reserva",
            message=f"Estimado/a {reserva.idCliente.first_name},\n\n"
                f"Lamentamos informarle que su reserva para el día {fecha} ha sido cancelada. Su pago sera reenvolsado de inmediato \n\n"
                f"Saludos cordiales,\nEl equipo de Masajes."
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            return JsonResponse({"status": "error", "message": "Error sending email to " + reserva.idCliente.email}, status=500)
        reserva.delete()
        Fiestas.objects.create(fecha=fecha, empleado=worker, general=False)
        return JsonResponse({"status": "error"}, status=200)
