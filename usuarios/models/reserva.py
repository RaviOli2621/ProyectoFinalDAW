from django.db import models
from django.contrib.auth.models import User
from masajes.models import Masaje

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