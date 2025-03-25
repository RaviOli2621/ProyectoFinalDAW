from django.shortcuts import render
from .models import Masaje, TipoMasaje
from commons.utils import get_filename  # Importamos la función de utilidad

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