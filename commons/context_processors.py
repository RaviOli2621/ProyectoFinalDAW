from masajes.models import TipoMasaje
from django.conf import settings

def tipos_masajes(request):
    tipos = TipoMasaje.objects.all()
    return {'tipos_masajes': tipos}

def env_vars(request):
    """
    Expone las variables de entorno definidas en settings.ENV_VARS_FOR_TEMPLATES
    a todos los templates.
    """
    return settings.ENV_VARS_FOR_TEMPLATES
