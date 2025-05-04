from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django.utils import timezone
from django_q.tasks import async_task

class Command(BaseCommand):
    help = 'Configura las tareas programadas de la aplicación'

    def handle(self, *args, **kwargs):
        # Tarea diaria para ejecutar a medianoche (00:00)
        task, created = Schedule.objects.update_or_create(
            name='manage_reservations',
            defaults={
                'func': 'commons.tasks.manage_reservations',
                'schedule_type': Schedule.DAILY,
                'repeats': -1,  # -1 significa repetir indefinidamente
                'next_run': timezone.localtime(timezone.now()).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ) + timezone.timedelta(days=1),  # Próximo día a las 00:00
            }
        )
        
        # Ejecutar la tarea inmediatamente al iniciar
        if created:
            async_task('commons.tasks.manage_reservations')
            self.stdout.write(self.style.SUCCESS('Tarea ejecutada inmediatamente por primera vez'))
        
        self.stdout.write(self.style.SUCCESS('Tareas programadas configuradas correctamente'))
        
        # Puedes descomentar esta sección si necesitas la tarea adicional
        # Schedule.objects.update_or_create(
        #     name='recordatorio_reservas_diario',
        #     defaults={
        #         'func': 'commons.tasks.check_next_day_reservations',
        #         'schedule_type': Schedule.DAILY,
        #         'repeats': -1,
        #         'next_run': timezone.localtime(timezone.now()).replace(
        #             hour=20, minute=0, second=0, microsecond=0
        #         ),
        #     }
        # )
        
        self.stdout.write(self.style.SUCCESS('Tareas programadas configuradas correctamente'))