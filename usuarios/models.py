from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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