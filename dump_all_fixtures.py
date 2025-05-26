# dump_all_fixtures.py
import os

# Lista de modelos propios
MODELS = [
    # App usuarios
    'usuarios.UserProfile',
    'usuarios.Worker',
    'usuarios.Reserva',
    'usuarios.Fiestas',
    # App masajes
    'masajes.Masaje',
    'masajes.TipoMasaje',
    # Django auth
    'auth.User',
    'auth.Group',
    'auth.Permission',
    # Django-Q
    'django_q.Schedule',
    'django_q.Failure',
    'django_q.Success',
    'django_q.Task',
]

os.makedirs('fixtures', exist_ok=True)

for model in MODELS:
    filename = f"fixtures/{model.replace('.', '_')}.json"
    print(f"Exportando {model} a {filename} ...")
    os.system(f'python manage.py dumpdata {model} --indent 2 > {filename}')