from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from masajes.models import Masaje

# Modal datos extra usuario
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación 1 a 1 con User
    foto = models.ImageField(upload_to="usuarios/static/fotosPerfil/", blank=True, null=True)

    def __str__(self):
        return self.user.username

# Cuando se crea un nuevo usuario, genera un perfil vinculado.   
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Cada vez que el usuario se guarda, también se guarda su perfil.
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Worker(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='worker')
    dni = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.dni}"


class Reserva(models.Model):
    fecha = models.DateTimeField()  # Automatically set the field to now when the object is created
    idCliente = models.ForeignKey(User, on_delete=models.CASCADE)  # Relación 1 a 1 con User
    idMasaje = models.ForeignKey(Masaje, on_delete=models.CASCADE)
    duracion = models.DurationField()  # Campo para almacenar la duración del masaje
    pagado = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=10, choices=[('efectivo', 'Efectivo'), ('targeta', 'Tarjeta')],default="efectivo")

    def __str__(self):
        return self.idCliente.username + " - " + self.idMasaje.nombre