import datetime
from django.db import models

class TipoMasaje(models.Model):
    nombre = models.CharField(max_length=50)
    description = models.TextField(blank=True,max_length=200)
    foto = models.ImageField(blank=True,upload_to="masajes/static/masajes/",default="default.jpg")

    def __str__(self):
        return self.nombre

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id)