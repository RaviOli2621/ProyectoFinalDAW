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