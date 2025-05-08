import datetime
from functools import wraps
import os
from django.conf import settings
from django.utils import timezone  
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from commons.forms import EnviarCorreoForm
from commons.services.email_service import send_email
from djangoProject.settings import EMAIL_SERVICE
from usuarios.models import Reserva
from masajes.models import Masaje  

def token_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        token = request.GET.get('token') or request.headers.get('Authorization')
        
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
        
        if token != settings.DAILY_TASK_TOKEN:
            return HttpResponseForbidden("Acceso denegado: token no válido")
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view

def home(request):
    from django.templatetags.static import static

    imagen_default = 'masajes/crayones.jpg'  

    masajes = Masaje.objects.all()
    carrusel_items = []
    for masaje in masajes:
        if masaje.foto:  
            img_url = f"masajes/{os.path.basename(str(masaje.foto))}"
        else:
            img_url = imagen_default
        carrusel_items.append({
            "id": masaje.id,
            "titulo": masaje.nombre,
            "img_url": img_url,
        })

    return render(request, "home.html", {
        "carrusel_items": carrusel_items,
    })

def enviar_correo(request):
    if request.method == 'POST':
        form = EnviarCorreoForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            cuerpo = form.cleaned_data['cuerpo']
            success = correo(titulo,cuerpo,form.cleaned_data['asunto'],form.cleaned_data['correo_usuario'],EMAIL_SERVICE)
            context = {
                'form': form,
                'toastType': 'success' if success else 'error',
                'toastTxt': "Correo enviado exitosamente" if success else "Error al enviar el correo"
            }
            return render(request, 'contacta.html', context)
        else:
            errores = " ".join(
                [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
            )
            return render(request, 'contacta.html', {
                'form': form,
                'toastTxt': f"Error al enviar el correo, {errores}",
                'toastType': 'error'
            })
    else:
        form = EnviarCorreoForm()

    return render(request, 'contacta.html', {'form': form})

def correo(titulo, cuerpo, asunto, loEnvia, destinatario):
    mensaje_texto = f"{titulo}\n\n{cuerpo}"
    
    contenido_formateado = cuerpo.replace('\n', '<br>')
    mensaje_html = f"""
        <h1>{titulo}</h1>
        <div>{contenido_formateado}</div>
        """
    
    success = send_email(
        subject=asunto,
        message=mensaje_texto,
        html_message=mensaje_html,  
        to_emails=[destinatario],
        from_email=loEnvia,
        signature_email=loEnvia,
        add_signature=True
    )
    
    return success

@token_required
def test_daily(request):
    """Tarea principal que ejecuta las subtareas programadas"""
    usuarios_mañana = notificar_usuarios_reservas_mañana()
    
    trabajadoresEl = eliminar_trabajadores_vencidos()

    eliminadas = eliminar_reservas_pasadas()
    
    return HttpResponse(f"Se notificaron {len(usuarios_mañana)} usuarios con reservas para mañana " \
           f"y se eliminaron {eliminadas} reservas antiguas." \
           f" Trabajadores eliminados: {trabajadoresEl['trabajadores_eliminados']}.") 

def notificar_usuarios_reservas_mañana():
    """Notifica a usuarios con reservas programadas para el día siguiente"""
    usuarios = get_usuarios_reservas_mañana()
    
    for usuario, reservas in usuarios.items():
        detalles_reservas = "\n".join([
            f"- Masaje número {reserva.id} llamado {reserva.idMasaje.nombre} a las {reserva.fecha.strftime('%H:%M')}" 
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
    fecha_limite = timezone.now().date() - timezone.timedelta(days=dias)
    
    resultado = Reserva.objects.filter(fecha__lt=fecha_limite).delete()
    
    return resultado[0] if resultado and isinstance(resultado, tuple) else 0

def get_usuarios_reservas_mañana():
    mañana = timezone.now().date() + timezone.timedelta(days=1)
    print(f"Buscando reservas para: {mañana}")
    
    inicio_mañana = timezone.make_aware(datetime.datetime.combine(mañana, datetime.time.min))
    fin_mañana = timezone.make_aware(datetime.datetime.combine(mañana, datetime.time.max))
    
    print(f"Rango de búsqueda: {inicio_mañana} hasta {fin_mañana}")
    
    reservas_mañana = Reserva.objects.filter(fecha__range=(inicio_mañana, fin_mañana))
    print(f"Reservas encontradas: {reservas_mañana.count()}")
    
    usuarios_reservas = {}
    for reserva in reservas_mañana:
        if reserva.idCliente not in usuarios_reservas:
            usuarios_reservas[reserva.idCliente] = []
        usuarios_reservas[reserva.idCliente].append(reserva)
    
    return usuarios_reservas

def eliminar_trabajadores_vencidos():
    from usuarios.models import Worker
    from django.contrib.auth.models import User
    
    hoy = timezone.now().date()
    
    print(f"Buscando trabajadores con fecha de eliminación vencida (hoy es {hoy})")
    
    trabajadores_vencidos = Worker.objects.filter(delete_date__lte=hoy)
    cantidad_trabajadores = trabajadores_vencidos.count()
    print(f"Encontrados {cantidad_trabajadores} trabajadores a eliminar")
    
    usuarios_eliminados = 0
    trabajadores_eliminados = 0
    
    for trabajador in trabajadores_vencidos:
        print(f"Procesando trabajador: {trabajador.id} - {trabajador.user_profile.user.username}")
        
        if hasattr(trabajador, 'idUsuario') and trabajador.idUsuario:
            usuario = trabajador.idUsuario
            print(f"  → Eliminando usuario asociado: {usuario.username}")
            
            try:
                usuario.delete()
                usuarios_eliminados += 1
                print(f"  ✓ Usuario eliminado correctamente")
            except Exception as e:
                print(f"  ✗ Error al eliminar usuario: {str(e)}")
        
        try:
            trabajador.delete()
            trabajadores_eliminados += 1
            print(f"  ✓ Trabajador eliminado correctamente")
        except Exception as e:
            print(f"  ✗ Error al eliminar trabajador: {str(e)}")
    
    mensaje = f"Proceso completado: {trabajadores_eliminados} trabajadores y {usuarios_eliminados} usuarios eliminados."
    
    print(mensaje)
    return {
        "trabajadores_eliminados": trabajadores_eliminados,
        "usuarios_eliminados": usuarios_eliminados,
        "mensaje": mensaje
    }
