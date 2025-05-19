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

    @classmethod
    def existe_general_en_fecha(cls, fecha):
        return cls.objects.filter(fecha=fecha, general=True).exists()

    @classmethod
    def existe_personal_en_fecha(cls, fecha, empleado_id):
        return cls.objects.filter(fecha=fecha, general=False, empleado_id=empleado_id).exists()

    @classmethod
    def get_personal_en_fecha(cls, fecha, empleado):
        return cls.objects.filter(fecha=fecha, empleado=empleado).first()

    @classmethod
    def get_festivos_personales(cls, fecha, workers_ids):
        return cls.objects.filter(
            fecha=fecha,
            general=False,
            empleado_id__in=workers_ids
        ).count()

    @classmethod
    def crear_general(cls, fecha):
        return cls.objects.create(fecha=fecha, general=True)

    @classmethod
    def crear_personal(cls, fecha, empleado):
        return cls.objects.create(fecha=fecha, empleado=empleado, general=False)

    @classmethod
    def eliminar_general(cls, fecha):
        return cls.objects.filter(fecha=fecha, general=True).delete()

    @classmethod
    def eliminar_personal(cls, fecha, empleado):
        return cls.objects.filter(fecha=fecha, empleado=empleado).delete()