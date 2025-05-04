import datetime
from django.utils import timezone  
from django.http import HttpResponse
from django.shortcuts import render
from commons.forms import EnviarCorreoForm
from commons.services.email_service import send_email
from djangoProject.settings import EMAIL_SERVICE
from usuarios.models import Reserva

def home(request):
    return render(request, 'home.html')

def enviar_correo(request):
    if request.method == 'POST':
        form = EnviarCorreoForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            cuerpo = form.cleaned_data['cuerpo']
            success = correo(titulo,cuerpo,form.cleaned_data['asunto'],form.cleaned_data['correo_usuario'],EMAIL_SERVICE)
            # Versión de texto plano

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
    # Versión de texto plano
    mensaje_texto = f"{titulo}\n\n{cuerpo}"
    
    # Versión HTML con formato
    contenido_formateado = cuerpo.replace('\n', '<br>')
    mensaje_html = f"""
        <h1>{titulo}</h1>
        <div>{contenido_formateado}</div>
        """
    
    success = send_email(
        subject=asunto,
        message=mensaje_texto,
        html_message=mensaje_html,  # Añadir versión HTML
        to_emails=[destinatario],
        from_email=loEnvia,
        signature_email=loEnvia,
        add_signature=True
    )
    
    return success

def test_daily(request):

    return HttpResponse("Siu")
    