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
import json

def worker_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        # Refactor: usa método del modelo
        if not Worker.is_user_worker(request.user):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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
        reserva.foto_nombre = get_filename(reserva.idMasaje.foto) 
        reserva.duracion_formatada = f"{reserva.idMasaje.duracion.total_seconds() / 3600:.1f}"  
        reserva.precio_final = float(reserva.idMasaje.precio) * float(reserva.duracion_formatada)

    return render(request,"reserves.html",{
        "reserves": reserves
    })

@worker_required
def workerReserves(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            idReserva = data.get('reserva_id')
            pagado = data.get('pagado')
            hecho = data.get('hecho')
            reserva = Reserva.objects.get(id=idReserva)
            reserva.pagado = pagado
            reserva.hecho = hecho
            reserva.save()
            return JsonResponse({'success': False})
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return render(request,"workerReservas.html",{
        })

def getReservaById(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        reserva_id = data.get('reserva_id')
        reserva = get_object_or_404(Reserva, id=reserva_id)
        return JsonResponse({
            'fecha': reserva.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'masajePrecio': reserva.idMasaje.precio,
            'duracion': reserva.duracion.total_seconds(),
            'metodo_pago': reserva.metodo_pago,
            'pagado': reserva.pagado,
            'id': reserva_id,
            'titulo': reserva.idMasaje.nombre,
            'foto': reserva.idMasaje.foto.name,
            'hecho': reserva.hecho,
        })

@login_required
def reservar(request):
    masaje_id = request.GET.get('masajeId')  
    
    if not masaje_id:
        return redirect('home')  

    try:
        masaje = Masaje.objects.get(id=masaje_id)
    except Masaje.DoesNotExist:
        return redirect('home')  

    if request.method == 'POST':
        reserva_form = ReservaForm(request.POST)

        if reserva_form.is_valid():
            metodo_pago = reserva_form.cleaned_data['metodo_pago']

            # Si el método de pago es targeta guardar la reserva temporalmente en la sesión
            if metodo_pago == 'targeta':
                reserva_temp = reserva_form.cleaned_data
                
                reserva_temp['fecha'] = reserva_temp['fecha'].strftime('%Y-%m-%d %H:%M:%S')  
                reserva_temp['idCliente'] = request.user.id  
                
                reserva_temp['idMasaje'] = masaje.id  
                
                reserva_temp['duracion'] = reserva_temp['duracion'].total_seconds()  
                
                request.session['reserva_temp'] = reserva_temp
                return redirect('pago_tarjeta')  

            # Si el método de pago es efectivo guardar la reserva
            
            reserva = reserva_form.save(commit=False)
            reserva.idCliente = request.user  
            reserva.idMasaje = masaje  
            reserva.duracion = None  
            reserva.save()
            return redirect('reservas') 

    else:
        reserva_form = ReservaForm()
        reserva_form.fields['duracion'].initial = masaje.duracion  

    return render(request, 'reservar.html', {'reserva_form': reserva_form, 'masaje': masaje})

@login_required
def pago_tarjeta(request):
    reserva_temp = request.session.get('reserva_temp', None)

    if not reserva_temp:
        return redirect('crear_reserva')  # Si no hay reserva temporal, redirige al formulario de reserva
    
    if request.method == 'POST':
        tarjeta_form = TarjetaForm(request.POST)
        
        if tarjeta_form.is_valid():
            fecha = datetime.strptime(reserva_temp['fecha'], '%Y-%m-%d %H:%M:%S')  
            
            id_masaje = reserva_temp['idMasaje']
            masaje = Masaje.objects.get(id=id_masaje)  
            

            id_cliente = reserva_temp['idCliente']
            cliente = User.objects.get(id=id_cliente)  
            
            reserva = Reserva(
                fecha=fecha,
                idMasaje=masaje,  
                metodo_pago=reserva_temp['metodo_pago'],
                idCliente=cliente,  
                pagado=True, 
            )
            reserva.save()  

            del request.session['reserva_temp']

            return redirect('confirmacion_pago')  

    else:
        tarjeta_form = TarjetaForm()

    return render(request, 'tarjeta_template.html', {'tarjeta_form': tarjeta_form})

@login_required
def editar_reserva(request):
    reserva_id = request.GET.get('reservaid')  

    reserva = get_object_or_404(Reserva, id=reserva_id)
    if reserva.idCliente.id != request.user.id:
        return redirect('home')  
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
                reserva_temp['reserva_id'] = reserva.id  
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
            id_cliente = reserva_temp['idCliente']
            cliente = User.objects.get(id=id_cliente)
            reserva_id = reserva_temp['reserva_id']
            reserva = get_object_or_404(Reserva, id=reserva_id) 
            reserva.fecha = fecha
            reserva.idMasaje = masaje
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
        reserva = get_object_or_404(Reserva, id=reserva_id)
        
        try:
            reserva.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)