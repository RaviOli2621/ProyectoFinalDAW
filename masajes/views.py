from datetime import datetime, timedelta 
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.forms import ReservaForm, TarjetaForm
from usuarios.models import Reserva
from .models import Masaje, TipoMasaje
from commons.utils import get_filename  # Importamos la función de utilidad
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # Import User model

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

@login_required
def reserves(request):
    return render(request,"masajes.html",{
        "id":request.user.id
    })

@login_required
def reservar(request):
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
                reserva_temp['idMasaje'] = reserva_temp['idMasaje'].id  # Guardamos el ID de Masaje
                
                # Convertir la duración a segundos (timedelta a número entero)
                reserva_temp['duracion'] = reserva_temp['duracion'].total_seconds()  # Convertimos la duración a segundos
                
                request.session['reserva_temp'] = reserva_temp
                return redirect('pago_tarjeta')  # Redirige al formulario de pago con tarjeta
            
            # Si el método de pago es "efectivo", simplemente guarda la reserva
            reserva = reserva_form.save(commit=False)
            reserva.idCliente = request.user  # Asocia la reserva al usuario actual
            reserva.save()
            return redirect('home')  # Redirige a la página de inicio (home) después de guardar la reserva

    else:
        reserva_form = ReservaForm()

    return render(request, 'reservar.html', {'reserva_form': reserva_form})

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
            duracion = timedelta(seconds=reserva_temp['duracion'])  # Usamos timedelta correctamente

            # Obtener la instancia del usuario usando el ID almacenado en la sesión
            id_cliente = reserva_temp['idCliente']
            cliente = User.objects.get(id=id_cliente)  # Recuperamos la instancia de User usando el ID
            
            # Crear y guardar la reserva
            reserva = Reserva(
                fecha=fecha,
                idMasaje=masaje,  # Usamos la instancia de Masaje recuperada
                duracion=duracion,  # Usamos la duración convertida a timedelta
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


