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
        masajes = Masaje.get_by_tipo(tipo_id)
        verTipo = False
        tipos = TipoMasaje.get_by_id(tipo_id)
    else:
        masajes = Masaje.get_all()
        tipos = TipoMasaje.get_all()

    for masaje in masajes:
        masaje.foto_nombre = get_filename(masaje.foto)  

    for tipo in tipos:
        tipo.foto_nombre = get_filename(tipo.foto)  

    return render(request, 'masajes.html', {
        'masajes': masajes,
        'tipos': tipos,
        "verTipo": verTipo
    })

def masaje(request):
    id = request.GET.get('tipo')
    masaje = Masaje.get_by_id(id)
    if masaje:
        masaje.foto_nombre = get_filename(masaje.foto)
        return render(request, 'masaje.html', {
            "masaje": masaje,
        })  
    else:
        return redirect('home')