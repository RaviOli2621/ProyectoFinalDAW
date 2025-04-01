from http.client import HTTPResponse
from django.shortcuts import render
from django.core.mail import send_mail
from commons.forms import EnviarCorreoForm
from django.conf import settings

from djangoProject.settings import EMAIL_SERVICE  # Para acceder a las configuraciones

# Create your views here.

def home(request):
    return render(request,'home.html')

def enviar_correo(request):
    if request.method == 'POST':
        form = EnviarCorreoForm(request.POST)
        if form.is_valid():
            correo_usuario = form.cleaned_data['correo_usuario']
            asunto = form.cleaned_data['asunto']
            cuerpo = form.cleaned_data['cuerpo']
            
            # Agregar "firmado" con el correo del usuario al final del cuerpo
            cuerpo += f"\n\nFirmado,\n{correo_usuario}"
            
            # Enviar el correo
            send_mail(
                asunto,
                cuerpo,
                EMAIL_SERVICE,  # Correo de servicio desde donde se enviará
                [EMAIL_SERVICE],  # Correo del usuario
                fail_silently=False,
            )
            return render(request, 'home.html')  # Redirige a una página de éxito
    else:
        form = EnviarCorreoForm()

    return render(request, 'contacta.html', {'form': form})