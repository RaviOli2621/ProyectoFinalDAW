import datetime
from django.db import models

from .tipoMasaje import TipoMasaje

class Masaje(models.Model):
    nombre = models.CharField(max_length=50)
    descriptionSh = models.TextField(blank=True,max_length=250,default="")
    description = models.TextField(blank=True,max_length=750,default="")
    foto = models.ImageField(blank=True,upload_to="masajes/static/masajes/",default="default.jpg")
    precio = models.DecimalField(max_digits=6, decimal_places=2,default=0.00)
    tipo = models.ForeignKey(TipoMasaje, on_delete=models.CASCADE,null=True)
    duracion = models.DurationField(default=datetime.timedelta(hours=1))  

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_tipo(cls, tipo_id):
        return cls.objects.filter(tipo_id=tipo_id)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.filter(id=id).first()

    def __str__(self):
        return self.nombre