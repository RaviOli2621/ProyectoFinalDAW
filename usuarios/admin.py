from django.contrib import admin

from usuarios.models import Reserva, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Reserva)
