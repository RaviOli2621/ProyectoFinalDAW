import datetime
from django.db import models

class TipoMasaje(models.Model):
    nombre = models.CharField(max_length=50)
    description = models.TextField(blank=True,max_length=200)
    foto = models.ImageField(blank=True,upload_to="masajes/static/masajes/",default="default.jpg")

    def __str__(self):
        return self.nombre
    
class Masaje(models.Model):
    nombre = models.CharField(max_length=50)
    descriptionSh = models.TextField(blank=True,max_length=250,default="")
    description = models.TextField(blank=True,max_length=750,default="")
    foto = models.ImageField(blank=True,upload_to="masajes/static/masajes/",default="default.jpg")
    precio = models.DecimalField(max_digits=6, decimal_places=2,default=0.00)
    tipo = models.ForeignKey(TipoMasaje, on_delete=models.CASCADE,null=True)
    duracion = models.DurationField(default=datetime.timedelta(hours=1))  


    def __str__(self):
        return self.nombre
    