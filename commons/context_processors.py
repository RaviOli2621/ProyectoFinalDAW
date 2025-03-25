from masajes.models import TipoMasaje

def tipos_masajes(request):
    return {
        'tipos_masajes': TipoMasaje.objects.all()  # Esto hará que los tipos de masajes estén disponibles en todas las plantillas
    }
