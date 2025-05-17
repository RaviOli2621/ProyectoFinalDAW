from django.db import models
from .worker import Worker

class Fiestas(models.Model):
    fecha = models.DateField()
    general = models.BooleanField(default=False)  
    empleado = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)  

    def __str__(self):
        if self.general:
            return str(self.fecha) + " - General"
        else:
            return str(self.fecha) + " - " + str(self.empleado)