from django.contrib import admin

from usuarios.models import Reserva, UserProfile, Worker

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Worker)
admin.site.register(Reserva)
