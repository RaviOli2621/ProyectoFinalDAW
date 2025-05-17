import cloudinary
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary_storage.storage import MediaCloudinaryStorage as CloudinaryStorage

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    foto = models.ImageField(upload_to="usuarios/fotosPerfil/", storage=CloudinaryStorage(), blank=True, null=True)

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

    @classmethod
    def get_or_create_by_user(cls, user):
        return cls.objects.get_or_create(user=user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()