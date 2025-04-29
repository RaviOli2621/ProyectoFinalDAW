from datetime import datetime, time, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.forms import ReservaForm, TarjetaForm
from usuarios.models import Fiestas, Reserva, Worker
from .models import Masaje, TipoMasaje
from commons.utils import get_filename  # Importamos la función de utilidad
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Import User model
from django.utils.timezone import make_aware, is_naive
import os
import glob
# Function to dynamically import all view modules in the current directory
def import_views_from_directory(directory):
    view_files = glob.glob(os.path.join(directory, "*.py"))
    for view_file in view_files:
        module_name = os.path.basename(view_file)[:-3]
        if module_name != "__init__":
            __import__(f"masajes.{module_name}")

# Import all views from the current directory
current_directory = os.path.dirname(__file__)
import_views_from_directory(current_directory)
# decorador para cuando no estas logado
def notAdmin_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

@notAdmin_user
def calendari(request):
    return render(request,"masajes.html")

def safe_aware(dt):
    if is_naive(dt):
        return make_aware(dt)
    return dt

def calcDiaCalendario(dia_evento, current_date, workers, delta):
    # Comprobar si es fiesta general
    if Fiestas.objects.filter(fecha=current_date, general=True).exists():
        dia_evento["color"] = "gray"
        current_date += delta
        return dia_evento
        
    # Calcular trabajadores disponibles ese día (fiestas personales)
    festivos_personales = Fiestas.objects.filter(fecha=current_date, general=False).count()

    # Franja horaria: de 8:00 a 22:00 cada 30 minutos
    franjas = [
        safe_aware(datetime.combine(current_date, time(8, 0)) + timedelta(minutes=30 * i))
        for i in range(28)
    ]
    horas_ocupadas = 0
    for franja_inicio in franjas:
        franja_fin = franja_inicio + timedelta(minutes=30)


        workersThisHour = workers.filter(start_time__lte=franja_inicio.time())  # El trabajador empieza antes de la franja
        workersThisHour = workersThisHour.filter(end_time__gte=franja_fin.time())  # El trabajador acaba después de la franja
        total_workers = workersThisHour.count()
        workers_disponibles = total_workers - festivos_personales
        reservas = Reserva.objects.filter(
            fecha__lte=franja_inicio,
            fecha__gte=franja_inicio - timedelta(hours=3)  # margen para masajes largos
        )

        ocupacion = 0

        for r in reservas:
            inicio = r.fecha

            duracion = r.duracion or r.idMasaje.duracion
            fin = inicio + duracion

            if inicio < franja_fin and fin > franja_inicio:
                ocupacion += 1

        if ocupacion >= workers_disponibles:
            horas_ocupadas += 1

    # Clasificar el día según ocupación
    if horas_ocupadas == 0:
        dia_evento["backgroundColor"] = "green"
    elif horas_ocupadas < len(franjas):
        dia_evento["backgroundColor"] = "orange"
    else:
        dia_evento["backgroundColor"] = "red"
    return dia_evento

def calendario_api(request):
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

    current_date = start_date
    while current_date < end_date:
        dia_evento = {"start": current_date.isoformat(), "display": "background"}
       
        dia_evento = calcDiaCalendario(dia_evento, current_date, workers, delta)

        eventos.append(dia_evento)
        current_date += delta

    return JsonResponse(eventos, safe=False)

def horas_api(request):
    # Obtener el día seleccionado del calendario
    fecha_seleccionada = request.GET.get('fecha')
    fecha = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()

    # Crear un diccionario para almacenar las horas ocupadas
    horas_ocupadas = []

    franjas = [
    safe_aware(datetime.combine(fecha, time(8, 0)) + timedelta(minutes=30 * i))
    for i in range(28)
    ]
    workers = Worker.objects.filter(delete_date__isnull=True)

    for franja_inicio in franjas:
        franja_fin = franja_inicio + timedelta(minutes=30)
        reservas = Reserva.objects.filter(
            fecha__lte=franja_inicio,
            fecha__gte=franja_inicio - timedelta(hours=3)  # margen para masajes largos
        )
        workersThisHour = workers.filter(start_time__lte=franja_inicio.time())
        workersThisHour = workersThisHour.filter(end_time__gte=franja_fin.time())  
        total_workers = workersThisHour.count()
        horas_disponibles = total_workers

        for r in reservas:
            inicio = r.fecha  
            duracion = r.duracion if r.duracion else r.idMasaje.duracion
            fin = inicio + duracion

            if inicio < franja_fin and fin > franja_inicio:
                horas_disponibles -= 1
             
        if horas_disponibles <= 0:
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"red"})
        elif horas_disponibles < workersThisHour.count():
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"orange"})
        else:
            horas_ocupadas.append({"fecha":franja_inicio.isoformat(),"color":"green"})
    return JsonResponse(horas_ocupadas, safe=False)

@login_required
def reserves(request):
    idUser = request.user.id
    reserves = Reserva.objects.filter(idCliente=idUser)
    for reserva in reserves:
        reserva.foto_nombre = get_filename(reserva.idMasaje.foto)  # Extrae solo el nombre de la imagen
        reserva.duracion_formatada = f"{reserva.idMasaje.duracion.total_seconds() / 3600:.1f}"  # Convierte duración a horas con un decimal
        reserva.precio_final = float(reserva.idMasaje.precio) * float(reserva.duracion_formatada)

    return render(request,"reserves.html",{
        "reserves": reserves
    })

@login_required
def reservar(request):
    # Obtener el id del masaje desde la URL
    masaje_id = request.GET.get('masajeId')  # Obtiene el masajeId de la URL
    
    if not masaje_id:
        return redirect('home')  # Si no se pasa el idMasaje, redirige al home o muestra un error

    # Verificar que el masaje existe en la base de datos
    try:
        masaje = Masaje.objects.get(id=masaje_id)
    except Masaje.DoesNotExist:
        return redirect('home')  # Redirigir o mostrar un mensaje de error si el masaje no existe

    if request.method == 'POST':
        reserva_form = ReservaForm(request.POST)

        if reserva_form.is_valid():
            metodo_pago = reserva_form.cleaned_data['metodo_pago']

            # Si el método de pago es "targeta", guardamos la reserva temporalmente en la sesión
            if metodo_pago == 'targeta':
                reserva_temp = reserva_form.cleaned_data
                
                # Convertir la fecha a string para poder almacenarla en la sesión
                reserva_temp['fecha'] = reserva_temp['fecha'].strftime('%Y-%m-%d %H:%M:%S')  # Convertir fecha a string
                reserva_temp['idCliente'] = request.user.id  # Guardamos solo el ID del usuario en la sesión
                
                # Almacenar solo el ID del objeto Masaje en la sesión
                reserva_temp['idMasaje'] = masaje.id  # Usar el id de masaje que obtuvimos de la URL
                
                # Convertir la duración a segundos (timedelta a número entero)
                reserva_temp['duracion'] = reserva_temp['duracion'].total_seconds()  # Convertimos la duración a segundos
                
                request.session['reserva_temp'] = reserva_temp
                return redirect('pago_tarjeta')  # Redirige al formulario de pago con tarjeta

            # Si el método de pago es "efectivo", simplemente guarda la reserva
            
            reserva = reserva_form.save(commit=False)
            reserva.idCliente = request.user  # Asocia la reserva al usuario actual
            reserva.idMasaje = masaje  # Asocia el masaje seleccionado a la reserva
            reserva.duracion = None  # No guardar cambios en el campo duracion
            reserva.save()
            return redirect('reservas') 

    else:
        reserva_form = ReservaForm()
        reserva_form.fields['duracion'].initial = masaje.duracion  # Establecer la duración inicial en el formulario

    return render(request, 'reservar.html', {'reserva_form': reserva_form, 'masaje': masaje})

@login_required
def pago_tarjeta(request):
    reserva_temp = request.session.get('reserva_temp', None)

    if not reserva_temp:
        return redirect('crear_reserva')  # Si no hay reserva temporal, redirige al formulario de reserva
    
    if request.method == 'POST':
        tarjeta_form = TarjetaForm(request.POST)
        
        if tarjeta_form.is_valid():
            # Procesar el pago aquí (por ejemplo, con un servicio de pago externo)
            
            # Convertir la fecha de nuevo a un objeto datetime
            fecha = datetime.strptime(reserva_temp['fecha'], '%Y-%m-%d %H:%M:%S')  # Usamos datetime.strptime correctamente
            
            # Obtener la instancia de Masaje usando el ID almacenado en la sesión
            id_masaje = reserva_temp['idMasaje']
            masaje = Masaje.objects.get(id=id_masaje)  # Recuperamos el objeto Masaje usando el ID
            
            # Convertir la duración de segundos a timedelta
            # duracion = timedelta(seconds=reserva_temp['duracion'])  # Usamos timedelta correctamente

            # Obtener la instancia del usuario usando el ID almacenado en la sesión
            id_cliente = reserva_temp['idCliente']
            cliente = User.objects.get(id=id_cliente)  # Recuperamos la instancia de User usando el ID
            
            # Crear y guardar la reserva
            reserva = Reserva(
                fecha=fecha,
                idMasaje=masaje,  # Usamos la instancia de Masaje recuperada
                # duracion=duracion,  # Usamos la duración convertida a timedelta
                metodo_pago=reserva_temp['metodo_pago'],
                idCliente=cliente,  # Usamos la instancia de User recuperada
                pagado=True,  # Suponemos que el pago es exitoso
            )
            reserva.save()  # Guardamos la reserva

            # Elimina los datos de la reserva temporal de la sesión
            del request.session['reserva_temp']

            return redirect('confirmacion_pago')  # Redirige a la confirmación del pago

    else:
        tarjeta_form = TarjetaForm()

    return render(request, 'tarjeta_template.html', {'tarjeta_form': tarjeta_form})

@login_required
def editar_reserva(request):
    reserva_id = request.GET.get('reservaid')  # Obtiene el masajeId de la URL

    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        reserva_form = ReservaForm(request.POST, instance=reserva)
        
        if reserva_form.is_valid():
            metodo_pago = reserva_form.cleaned_data['metodo_pago']

            if metodo_pago == 'targeta' and reserva.pagado == False:
                reserva_temp = reserva_form.cleaned_data
                reserva_temp['fecha'] = reserva_temp['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                reserva_temp['idCliente'] = request.user.id
                reserva_temp['idMasaje'] = reserva.idMasaje.id
                reserva_temp['duracion'] = reserva_temp['duracion'].total_seconds()
                reserva_temp['reserva_id'] = reserva.id  # Guardamos el ID de la reserva en la sesión
                request.session['reserva_temp'] = reserva_temp
                return redirect('pago_tarjeta_cambio')

            reserva_form.save()
            return redirect('reservas')
    else:
        reserva_form = ReservaForm(instance=reserva)

    return render(request, 'reservar.html', {'reserva_form': reserva_form, 'reserva': reserva})

@login_required
def editar_pago_tarjeta(request):
    reserva_temp = request.session.get('reserva_temp', None)

    if not reserva_temp:
        return redirect('home')
    
    if request.method == 'POST':
        tarjeta_form = TarjetaForm(request.POST)
        
        if tarjeta_form.is_valid():
            fecha = datetime.strptime(reserva_temp['fecha'], '%Y-%m-%d %H:%M:%S')
            id_masaje = reserva_temp['idMasaje']
            masaje = Masaje.objects.get(id=id_masaje)
            # duracion = timedelta(seconds=reserva_temp['duracion'])
            id_cliente = reserva_temp['idCliente']
            cliente = User.objects.get(id=id_cliente)
            reserva_id = reserva_temp['reserva_id']
            reserva = get_object_or_404(Reserva, id=reserva_id) 
            reserva.fecha = fecha
            reserva.idMasaje = masaje
            # reserva.duracion = duracion
            reserva.metodo_pago = reserva_temp['metodo_pago']
            reserva.idCliente = cliente
            reserva.pagado = True
            reserva.save()
            
            del request.session['reserva_temp']
            return redirect('confirmacion_pago')
    else:
        tarjeta_form = TarjetaForm()

    return render(request, 'tarjeta_template.html', {'tarjeta_form': tarjeta_form})


def masajes(request):
    tipo_id = request.GET.get('tipo')
    verTipo = True
    
    if tipo_id:
        masajes = Masaje.objects.filter(tipo_id=tipo_id)
        verTipo = False
        tipos = TipoMasaje.objects.filter(id=tipo_id)  

    else:
        masajes = Masaje.objects.all()
        tipos = TipoMasaje.objects.all()  # Obtener todos los tipos de masajes

    # Aplicar `get_filename()` a cada objeto
    for masaje in masajes:
        masaje.foto_nombre = get_filename(masaje.foto)  # Extrae solo el nombre de la imagen

    for tipo in tipos:
        tipo.foto_nombre = get_filename(tipo.foto)  # También extrae el nombre de la imagen de TipoMasaje

    return render(request, 'masajes.html', {
        'masajes': masajes,
        'tipos': tipos,
        "verTipo": verTipo
    })

def masaje(request):
    id = request.GET.get('tipo')
    masaje = Masaje.objects.filter(id=id).first()
    masaje.foto_nombre = get_filename(masaje.foto)
    if id:
        return render(request, 'masaje.html', {
            "masaje": masaje,
        })  
    else:
        return redirect('home')

# Funciones para AJAX,etc
@login_required
def borrar_reserva(request, reserva_id):
    if request.method == 'POST':
        # Obtiene la reserva con el ID proporcionado, o devuelve un 404 si no existe.
        reserva = get_object_or_404(Reserva, id=reserva_id)
        
        try:
            # Eliminar la reserva
            reserva.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            # En caso de error al eliminar
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)