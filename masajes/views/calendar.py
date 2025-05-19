from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.forms import ReservaForm, TarjetaForm
from usuarios.models import Fiestas, Reserva, Worker
from masajes.models import Masaje, TipoMasaje
from commons.utils import get_filename  
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  
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
def calcDiaCalendario(dia_evento, current_date, workers, delta, blue,duracion):
    if current_date <= datetime.now().date():
        dia_evento["backgroundColor"] = "red"
        return dia_evento

    if current_date.weekday() in {5, 6}:
        dia_evento["color"] = "gray"
        return dia_evento
    if Fiestas.existe_general_en_fecha(current_date):
        dia_evento["color"] = "blue" if blue else "gray"
        return dia_evento

    franjas = [
        safe_aware(datetime.combine(current_date, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    franjas = quitarHorasDeDescanso(franjas)

    horas_ocupadas = 0
    ocupacionGeneral = 0
    for franja_inicio in franjas:
        duracionFormated = 30  
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
                duracionFormated = int(duracion)
            else:
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        duracionFormated = 30  
        
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
                duracionFormated = int(duracion)
            else:
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        workersThisHour = workers.filter(
            start_time__lt=franja_fin.time(),
            end_time__gt=franja_inicio.time()
        )
        total_workers = workersThisHour.count()

        festivos_personales = Fiestas.get_festivos_personales(
            current_date,
            list(workersThisHour.values_list('id', flat=True))
        )

        workers_disponibles = total_workers - festivos_personales

        reservas = Reserva.get_before(franja_inicio)

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
    year = int(request.GET.get('year', request.GET['year']))
    month = int(request.GET.get('month', request.GET['month']))
    blue = request.GET.get('blue', request.GET.get('blue', True))
    duradacion = request.GET.get('duracion', request.GET.get('duracion', 30))
    start_date = datetime(year, month, 1).date()
    end_date = (start_date.replace(day=28) + timedelta(days=10)).replace(day=1)
    delta = timedelta(days=1)

    workers = Worker.get_active_workers()

    current_date = start_date
    while current_date < end_date:
        dia_evento = {"start": current_date.isoformat(), "display": "background"}
        dia_evento = calcDiaCalendario(dia_evento, current_date, workers, delta, blue, duradacion)
        eventos.append(dia_evento)
        current_date += delta

    return JsonResponse(eventos, safe=False)
def horas_api(request):
    fecha_seleccionada = request.GET.get('fecha')
    duracion = request.GET.get('duracion')
    fecha = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()

    horas_ocupadas = []

    franjas = [
        safe_aware(datetime.combine(fecha, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    workers = Worker.get_active_workers()
    franjas = quitarHorasDeDescanso(franjas)
    for franja_inicio in franjas:
        duracionFormated = 30  
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
                duracionFormated = int(duracion)
            else:
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        # SOLO este cambio: usa método del modelo para reservas en la franja
        reservas = Reserva.get_for_time_window(franja_inicio)
        workersThisHour = Worker.get_available_workers_for_time(franja_inicio.time(), franja_fin.time())
        total_workers = workersThisHour.count()
        horas_disponibles = total_workers

        for r in reservas:
            inicio = r.fecha  
            duracion_r = r.duracion if r.duracion else r.idMasaje.duracion
            fin = inicio + duracion_r

            if inicio < franja_fin and fin > franja_inicio:
                horas_disponibles -= 1
             
        if horas_disponibles <= 0:
            horas_ocupadas.append({"fecha": franja_inicio.isoformat(), "color": "red"})
        elif horas_disponibles < workersThisHour.count():
            horas_ocupadas.append({"fecha": franja_inicio.isoformat(), "color": "orange"})
        else:
            horas_ocupadas.append({"fecha": franja_inicio.isoformat(), "color": "green"})
    return JsonResponse(horas_ocupadas, safe=False)
def quitarHorasDeDescanso(franjas):
    franjas = [franja for franja in franjas if franja.time() not in {time(13, 0),time(13, 30), time(19, 0),time(19, 30)}]
    return franjas

@require_http_methods(["PUT", "DELETE"])
def gestionarDiasFiesta(request):
    dia = request.GET.get('fecha')

    if request.method == "PUT":
        reservas = Reserva.get_for_day(dia)
        for reserva in reservas:
            from commons.services.email_service import send_email  
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
        Fiestas.crear_general(dia)
    elif request.method == "DELETE":
        Fiestas.eliminar_general(dia)
    return JsonResponse({"status": "success"}, status=200)
@notAdmin_user
def calendari(request):
    return render(request,"calendario.html")

def fiestaTrabajador(request):
    eventos = []
    year = int(request.GET.get('year', request.GET['year']))
    month = int(request.GET.get('month', request.GET['month']))

    start_date = datetime(year, month, 1).date()
    end_date = (start_date.replace(day=28) + timedelta(days=10)).replace(day=1)
    delta = timedelta(days=1)

    workers = Worker.get_active_workers()
    worker = Worker.get_by_id(request.GET.get('idTrabajador'))
    current_date = start_date
    while current_date < end_date:
        dia_evento = {"start": current_date.isoformat(), "display": "background"}
        dia_evento = calcFiestaTrabajador(dia_evento, current_date, workers, delta, worker)
        eventos.append(dia_evento)
        current_date += delta

    return JsonResponse(eventos, safe=False)
def calcFiestaTrabajador(dia_evento, current_date, workers, delta, worker):
    duracion = 30
    if worker is not None:
        worker_instance = worker
        if Fiestas.existe_personal_en_fecha(current_date, worker_instance.id):
            dia_evento["backgroundColor"] = "blue"
            return dia_evento

    if current_date <= datetime.now().date():
        dia_evento["backgroundColor"] = "red"
        return dia_evento

    if current_date.weekday() in {5, 6} or Fiestas.existe_general_en_fecha(current_date):
        dia_evento["color"] = "gray"
        return dia_evento

    franjas = [
        safe_aware(datetime.combine(current_date, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    franjas = quitarHorasDeDescanso(franjas)

    for franja_inicio in franjas:
        duracionFormated = 30 
        if duracion:
            if isinstance(duracion, str) and duracion.isdigit():
                duracionFormated = int(duracion)
            else:
                try:
                    time_parts = duracion.split(":")
                    hours = int(time_parts[0]) if len(time_parts) > 0 else 0
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                    duracionFormated = hours * 60 + minutes + (seconds // 60)
                except (ValueError, AttributeError, TypeError):
                    pass
        franja_fin = franja_inicio + timedelta(minutes=duracionFormated if duracion else 30)
        workersThisHour = Worker.exclude_worker_and_available_for_time(
            worker.id if worker else None,
            franja_inicio.time(),
            franja_fin.time()
        )
        total_workers = workersThisHour.count()
        reservas = Reserva.get_for_time_window(franja_inicio)

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

def cambiarFiestatrabajador(request, idTrabajador):
    fecha = request.GET.get('fecha')
    worker = Worker.get_by_id(idTrabajador)
    fiesta = Fiestas.get_personal_en_fecha(fecha, worker)

    workerHoraInicio = worker.start_time
    workerHoraFin = worker.end_time

    if fiesta:
        Fiestas.eliminar_personal(fecha, worker)
        return JsonResponse({"status": "success"}, status=200)
    else:
        hora_inicio = datetime.combine(datetime.strptime(fecha, "%Y-%m-%d"), workerHoraInicio)
        hora_fin = datetime.combine(datetime.strptime(fecha, "%Y-%m-%d"), workerHoraFin)

        reserva = Reserva.get_overlapping_reservation(fecha, hora_inicio, hora_fin)

        from commons.services.email_service import send_email  
        if reserva:
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
                return JsonResponse({"status": "error", "message": "Error enviando email al cliente."}, status=500)
            reserva.delete()
        Fiestas.crear_personal(fecha, worker)
        return JsonResponse({"status": "success"}, status=200)
