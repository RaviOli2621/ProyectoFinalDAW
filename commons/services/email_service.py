from django.core.mail import send_mail
from djangoProject.settings import EMAIL_SERVICE

def send_email(
    subject,
    message,
    to_emails,
    from_email=None,
    add_signature=True,
    signature_email=None,
    fail_silently=False,
    html_message=None
):
    """
    Función generalizada para enviar correos electrónicos.
    """
    # Si no se proporciona un remitente, usamos el configurado en settings
    if from_email is None:
        from_email = EMAIL_SERVICE
        
    # Añadir firma si se solicita
    if add_signature and signature_email:
        message += f"\n\nFirmado,\n{signature_email}"
    
    # Asegurarse de que to_emails sea una lista
    recipient_list = to_emails if isinstance(to_emails, list) else [to_emails]
    
    try:
        # Usar la función send_mail de Django
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently,
            html_message=html_message
        )
        return True
    except Exception as e:
        if not fail_silently:
            print(f"Error al enviar correo: {e}")
        return False