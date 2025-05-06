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
import json

def worker_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Verifica si existe un Worker asociado al usuario
        if not Worker.objects.filter(user_profile_id=request.user.id).exists():
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# decorador para cuando no estas logado
def notAdmin_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def safe_aware(dt):
    if is_naive(dt):
        return make_aware(dt)
    return dt

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

@worker_required
def workerReserves(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            idReserva = data.get('idReserva')
            pagado = data.get('pagado')
            reserva = get_object_or_404(Reserva, id=idReserva)
            reserva.pagado = pagado
            reserva.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request,"workerReservas.html",{
        })

def getReservaById(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id)
        print("Siu"+reserva.idMasaje.foto.name)
        return JsonResponse({
            'fecha': reserva.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'masajePrecio': reserva.idMasaje.precio,
            'duracion': reserva.duracion.total_seconds(),
            'metodo_pago': reserva.metodo_pago,
            'pagado': reserva.pagado,
            'id': reserva_id,
            'titulo': reserva.idMasaje.nombre,
            'foto': reserva.idMasaje.foto.name
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
    if reserva.idCliente.id != request.user.id:
        return redirect('home')  # Redirige al home si el usuario no es el propietario de la reserva
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
            print(reserva_form.errors)  
            reserva_form = ReservaForm(instance=reserva)
        
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