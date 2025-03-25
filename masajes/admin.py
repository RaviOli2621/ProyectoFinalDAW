from django.contrib import admin
from masajes.models import Masaje, TipoMasaje

# Register your models here.
admin.site.register(TipoMasaje)
admin.site.register(Masaje)