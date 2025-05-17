from django.db import models
from .user_profile import UserProfile
from django.contrib.auth.models import User
import datetime


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
    
    @classmethod
    def get_by_id(cls, worker_id):
        return cls.objects.filter(id=worker_id).first()

    @classmethod
    def get_active_workers(cls):
        return cls.objects.filter(delete_date__isnull=True)

    @classmethod
    def get_available_workers_for_time(cls, start_time, end_time):
        return cls.get_active_workers().filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        )

    @classmethod
    def exclude_worker_and_available_for_time(cls, worker_id, start_time, end_time):
        return cls.get_active_workers().exclude(id=worker_id).filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        )

    @classmethod
    def get_deleted_workers(cls):
        return cls.objects.filter(delete_date__isnull=False).order_by('-delete_date', "-delete_hour")

    @classmethod
    def mark_for_deletion_by_id(cls, worker_id):
        worker = cls.objects.get(id=worker_id)
        worker.delete_date = datetime.date.today() + datetime.timedelta(days=30)
        worker.save()
        return worker

    @classmethod
    def restore_first_deleted_worker(cls):
        worker = cls.objects.filter(delete_date__isnull=False).order_by('-delete_date', '-delete_hour').first()
        if worker:
            worker.delete_date = None
            worker.delete_hour = None
            worker.save()
            return worker
        return None

    @classmethod
    def mark_all_active_as_deleted(cls):
        today = datetime.date.today()
        for worker in cls.objects.filter(delete_date__isnull=True):
            worker.delete_date = today + datetime.timedelta(days=30)
            worker.save()

    @classmethod
    def create_or_update_from_profile(cls, profile, dni, phone, start_date, start_time, end_time):
        worker, created = cls.objects.get_or_create(user_profile=profile)
        worker.dni = dni
        worker.phone_number = phone
        worker.start_date = start_date
        worker.start_time = start_time
        worker.end_time = end_time
        worker.delete_date = None
        worker.save()
        return worker

    @classmethod
    def create_worker(cls, form):
        # Asume que el formulario ya está validado
        return form.save()

    def update_worker(self, form):
        # Asume que el formulario ya está validado
        return form.save()

    @classmethod
    def eliminar_trabajadores_vencidos(cls, fecha=None):
        from django.utils import timezone
        if fecha is None:
            fecha = timezone.now().date()
        trabajadores_vencidos = cls.objects.filter(delete_date__lte=fecha)
        trabajadores_eliminados = 0
        usuarios_eliminados = 0
        for trabajador in trabajadores_vencidos:
            usuario = trabajador.user_profile.user
            try:
                usuario.delete()
                usuarios_eliminados += 1
            except Exception:
                pass
            try:
                trabajador.delete()
                trabajadores_eliminados += 1
            except Exception:
                pass
        return {
            "trabajadores_eliminados": trabajadores_eliminados,
            "usuarios_eliminados": usuarios_eliminados
        }

    @classmethod
    def is_user_worker(cls, user):
        return cls.objects.filter(user_profile__user=user).exists()

    @classmethod
    def get_by_user_profile_id(cls, user_profile_id):
        return cls.objects.filter(user_profile_id=user_profile_id).first()

    @classmethod
    def exists_with_dni(cls, dni, exclude_pk=None):
        qs = cls.objects.filter(dni=dni)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
        return qs.exists()

    @classmethod
    def create_worker_from_form(cls, user_profile, cleaned_data):
        return cls.objects.create(
            user_profile=user_profile,
            dni=cleaned_data['dni'],
            phone_number=cleaned_data['phone_number'],
            start_date=cleaned_data['start_date'],
            start_time=cleaned_data['horario']['start_time'],
            end_time=cleaned_data['horario']['end_time']
        )

    def update_worker_from_form(self, cleaned_data):
        self.dni = cleaned_data['dni']
        self.phone_number = cleaned_data['phone_number']
        self.start_date = cleaned_data['start_date']
        self.start_time = cleaned_data['horario']['start_time']
        self.end_time = cleaned_data['horario']['end_time']
        self.save()
        return self

    @classmethod
    def get_users_without_pending_worker(cls):
        """
        Devuelve los usuarios que NO tienen un perfil de trabajador pendiente de borrar.
        """
        worker_user_ids = cls.objects.filter(
            delete_date__isnull=False
        ).values_list('user_profile__user', flat=True)
        return User.objects.all().exclude(id__in=worker_user_ids).order_by('id')