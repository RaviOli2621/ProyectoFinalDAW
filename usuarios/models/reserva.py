from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from masajes.models import Masaje
from django.db.models import F, ExpressionWrapper, DateTimeField

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

    @classmethod
    def get_by_cliente(cls, user_id):
        return cls.objects.filter(idCliente=user_id)

    @classmethod
    def get_by_id(cls, reserva_id):
        return cls.objects.filter(id=reserva_id).first()

    @classmethod
    def get_for_date_range(cls, start, end):
        return cls.objects.filter(fecha__range=(start, end))

    @classmethod
    def delete_older_than(cls, fecha_limite):
        return cls.objects.filter(fecha__lt=fecha_limite).delete()

    @classmethod
    def get_for_day(cls, dia):
        return cls.objects.filter(fecha__date=dia)

    @classmethod
    def get_before(cls, dt):
        """Reservas con fecha anterior o igual a dt."""
        return cls.objects.filter(fecha__lte=dt)

    @classmethod
    def get_in_window(cls, start, end):
        """Reservas entre start y end (ambos inclusive)."""
        return cls.objects.filter(fecha__gte=start, fecha__lt=end)

    @classmethod
    def get_for_time_window(cls, start, end=None):
        """
        Si solo se pasa start: reservas en las 3h anteriores a start.
        Si se pasa end: reservas entre start y end.
        """
        if end is not None:
            return cls.get_in_window(start, end)
        else:
            return cls.objects.filter(fecha__lte=start, fecha__gte=start - timedelta(hours=3))

    @classmethod
    def get_overlapping_reservation(cls, fecha, hora_inicio, hora_fin):
        return cls.objects.annotate(
            fin_reserva=ExpressionWrapper(
                F('fecha') + F('duracion'),
                output_field=DateTimeField()
            )
        ).filter(
            fecha__date=fecha,
            fecha__lt=hora_fin,
            fin_reserva__gt=hora_inicio
        ).last()