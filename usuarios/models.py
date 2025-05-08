import cloudinary
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary_storage.storage import MediaCloudinaryStorage as CloudinaryStorage

from masajes.models import Masaje

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    foto = models.ImageField(upload_to="usuarios/fotosPerfil/",storage=CloudinaryStorage(), blank=True, null=True)

    def __str__(self):
        return self.user.username
    def save(self, *args, **kwargs):
        try:
            old = UserProfile.objects.get(pk=self.pk)
            if old.foto and old.foto != self.foto:
                public_id = old.foto.name.rsplit('.', 1)[0]  
                cloudinary.uploader.destroy(public_id)
        except UserProfile.DoesNotExist:
            pass  

        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

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
    delete_date = models.DateField(null=True, blank=True)  
    delete_hour = models.TimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.dni}"

    def delete(self, *args, **kwargs):
            user = self.user_profile.user
            result = super().delete(*args, **kwargs)
            user.delete()
            return result

class Reserva(models.Model):
    fecha = models.DateTimeField()
    idCliente = models.ForeignKey(User, on_delete=models.CASCADE)
    idMasaje = models.ForeignKey(Masaje, on_delete=models.CASCADE)
    duracion = models.DurationField(null=True, blank=True)  
    pagado = models.BooleanField(default=False)
    hecho = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=10, choices=[('efectivo', 'Efectivo'), ('targeta', 'Tarjeta')], default="efectivo")

    def save(self, *args, **kwargs):
        if not self.duracion and self.idMasaje_id:
            self.duracion = self.idMasaje.duracion
        super().save(*args, **kwargs)

    def __str__(self):
        return self.idCliente.username + " - " + self.idMasaje.nombre
    
class Fiestas(models.Model):
    fecha = models.DateField()
    general = models.BooleanField(default=False)  
    empleado = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        if(self.general):
            return str(self.fecha) + " - General"
        else:
            return str(self.fecha) + " - " + str(self.empleado)