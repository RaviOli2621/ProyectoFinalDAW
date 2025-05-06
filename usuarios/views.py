import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
import random
import string

from usuarios.forms import CustomLoginForm, CustomSignInForm, UserEditForm, WorkeCreaterForm, WorkerEditForm
from usuarios.models import UserProfile, Worker

# Create your views here.

# decorador para cuando no estas logado
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

@unauthenticated_user
def signup(request):
    if request.method == "GET": 
        authentication_form = CustomSignInForm()
        return render(request,'signup.html',{
            'form':authentication_form
        })    
    elif request.method == "POST": 
        authentication_form = CustomSignInForm(request.POST)
        if(request.POST['password2'] == request.POST['password1']):
            try:
                user = User.objects.create_user(username=request.POST['username'],email=request.POST['gmail'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect("home")
            except IntegrityError:
                errorText = "El usuario ya existe"
        else: errorText = "Las contraseñas no coinciden"
        return render(request,'signup.html',{
            'form':authentication_form,
            'toastTxt':errorText,
            "toastType": "error"
        })  

@login_required
def signout(request):
    logout(request)
    return redirect("home")

@unauthenticated_user
def signin(request):
    if request.method == "GET": 
        remembered_username = request.COOKIES.get('remembered_username', '')
        form = CustomLoginForm()  # Instancia vacía
        if remembered_username:
            form.fields['username'].initial = remembered_username
        return render(request, "signin.html", {'form': form,'remembered_username': remembered_username if 'remembered_username' in locals() else ''})

    elif request.method == "POST":
        form = CustomLoginForm(data=request.POST)  # IMPORTANTE: Usa "data=request.POST"

        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user is None:
            return render(request, "signin.html", {
                'form': form,  # Ahora mantiene los datos ingresados
                'toastTxt': "Usuario o contraseña incorrecta",
                "toastType": "error"
            })
        else: 
            login(request, user)
            if request.POST.get('remember_me', False):
                print(f"modongo")
                max_age = 30 * 24 * 60 * 60  # 30 días en segundos
                response = redirect('home')  # Reemplaza 'home' con tu nombre de URL para la página de inicio
                response.set_cookie('remembered_username', user.username, max_age=max_age)
                return response
            else:
                response = redirect('home')
                response.delete_cookie('remembered_username')
                return response    
@login_required
def editUser(request):
    if request.method == 'GET':
        # Usar el usuario actual en lugar de buscar un Worker
        user = request.user
        
        # Inicializar el formulario con los datos del usuario actual
        initial_data = {
            'username': user.username,
            'email': user.email,
        }
        
        form = UserEditForm(initial=initial_data)
        
        return render(request, "editUser.html", {
            "form": form,
            # El usuario y su perfil ya están disponibles en el template como request.user
        })
    elif request.method == 'POST':
        user = request.user
        form = UserEditForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            # Guardar cambios en el usuario
            user = form.save(commit=False)
            
            user.email = user._original_email if hasattr(user, '_original_email') else User.objects.get(id=user.id).email


            # Manejar la contraseña si se proporcionó una nueva
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
                
            user.save()
            
            # Actualizar foto de perfil si se proporcionó
            if 'foto' in request.FILES:
                user.userprofile.foto = request.FILES['foto']
                user.userprofile.save()
                print(f"URL de la imagen guardada: {user.userprofile.foto.url}")

            # Mantener la sesión del usuario después de cambiar la contraseña
            if password1:
                login(request, user)
                
            return redirect('home')
        else:
            return render(request, "editUser.html", {
                "form": form,
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# Admin users
@permission_required('auth.change_user')
def userList(request,user_id=""):
    if request.method == "GET":
        all_users = User.objects.all()
        
        # Obtener los IDs de usuarios que ya son trabajadores
        worker_user_ids = Worker.objects.filter(
            delete_date__isnull=False  # Solo trabajadores activos
        ).values_list('user_profile__user', flat=False)
        
        # Filtrar para obtener solo usuarios que NO son trabajadores
        users = all_users.exclude(id__in=worker_user_ids)
        
        return render(request, "admin/userList.html",{
            "usuarios":users
        })
    elif request.method == 'POST':
        # Obtiene la reserva con el ID proporcionado, o devuelve un 404 si no existe.
        user = get_object_or_404(User, id=user_id)
        grupo = Group.objects.get(name="Administradores")
        if user.groups.filter(name="Administradores").exists():
            print("Si")
            user.groups.remove(grupo)
            user.save()
            return JsonResponse({'success': True})
        else:
            # Añadir usuario al grupo
            print("Siu")
            user.groups.add(grupo)
            user.save()
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# Admin workers

@permission_required('auth.change_user')
def workerList(request):
    workers = Worker.objects.filter(delete_date__isnull=True).order_by('id')

    return render(request, "admin/workerList.html", {
        "workers": workers
    })

@permission_required('auth.change_user')
def borrar_worker(request, worker_id):
    if request.method == 'POST':
        # Obtiene la reserva con el ID proporcionado, o devuelve un 404 si no existe.
        worker = get_object_or_404(Worker, id=worker_id)
        
        try:
            # Eliminar la reserva
            worker.delete_date = datetime.date.today() + datetime.timedelta(days=30)
            worker.delete_hour = datetime.datetime.now().time()
            worker.save()
            # worker.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            # En caso de error al eliminar
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def crear_worker(request):
    if request.method == 'GET':
        # Crear el formulario con la instancia del worker

        form = WorkeCreaterForm()
        
        return render(request, "admin/registerWorker.html", {
            "form": form,
        })
    elif request.method == 'POST':
        form = WorkeCreaterForm(request.POST,request.FILES)  
        
        if form.is_valid():
            form.save()
            return redirect('workerList')  # Redirige a la lista de trabajadores
        else:
            return render(request, "admin/registerWorker.html", {
                "form": form,
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def restore_worker(request):
    if request.method == 'POST':
        # Invertir el orden para que el último eliminado sea el primero en restaurarse
        workers = Worker.objects.filter(delete_date__isnull=False).order_by('-delete_date',"-delete_hour")
        worker = workers.first()
        if worker == None:
            return JsonResponse({'success': False, 'error': 'No hay trabajadores para restaurar'}, status=404)
        try:
            worker.delete_date = None
            worker.delete_hour = None
            worker.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def editar_worker(request):
    if request.method == 'GET':
        trabajador_id = request.GET.get('trabajador_id')
        if trabajador_id:
            worker = get_object_or_404(Worker, id=trabajador_id)
            
            # Crear el formulario con la instancia del worker

            form = WorkerEditForm(worker=worker)  # Pasamos el worker al formulario
            
            return render(request, "admin/editWorker.html", {
                "form": form,
                "worker": worker,  # Importante: pasar el worker al template
            })
        else:
            return JsonResponse({'success': False, 'error': 'ID de trabajador no proporcionado'}, status=400)
    elif request.method == 'POST':
        trabajador_id = request.POST.get('trabajador_id')
        if trabajador_id:
            worker = get_object_or_404(Worker, id=trabajador_id)

            form = WorkerEditForm(request.POST, request.FILES ,worker=worker)
            
            if form.is_valid():
                form.save()
                return redirect('workerList')  # Redirige a la lista de trabajadores
            else:
                return render(request, "admin/editWorker.html", {
                    "form": form,
                    "worker": worker,
                })
        else:
            return JsonResponse({'success': False, 'error': 'ID de trabajador no proporcionado'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@csrf_exempt
def importar_workers(request):
    if request.method == "POST":
        json_file = request.FILES.get('file')
        if not json_file:
            return JsonResponse({'error': 'No se subió ningún archivo'}, status=400)

        try:
            data = json.load(json_file)
        except Exception as e:
            return JsonResponse({'error': f'Formato JSON inválido: {str(e)}'}, status=400)

        resultados = {'creados': 0, 'actualizados': 0, 'errores': []}
        trabajadores_existentes = list(Worker.objects.values())
        for worker in trabajadores_existentes:
            if worker['delete_date'] is None:
                worker_instance = Worker.objects.get(id=worker['id'])
                worker_instance.delete_date = datetime.date.today() + datetime.timedelta(days=30)
                worker_instance.save()
        for entry in data:
            try:
                # Extraer campos obligatorios
                username = entry.get('username')
                if not username:
                    raise ValueError("El campo 'username' es obligatorio")
                
                dni = entry.get('dni')
                if not dni:
                    raise ValueError("El campo 'dni' es obligatorio")
                
                # Extraer otros campos con valores predeterminados
                phone = entry.get('phone_number', '')
                email = entry.get('email', '')
                password = entry.get('password', '')
                
                # FECHA: Manejar el campo start_date
                start_date_str = entry.get('start_date')
                if start_date_str:
                    try:
                        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        start_date = datetime.date.today()
                else:
                    start_date = datetime.date.today()
                
                # HORAS: Manejar explícitamente casos nulos o ausentes
                # Para start_time - usar valor predeterminado si no existe o es null
                start_time_str = entry.get('start_time')
                if start_time_str:
                    try:
                        start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
                    except ValueError:
                        start_time = datetime.time(9, 0)  # 9:00 AM predeterminado
                else:
                    start_time = datetime.time(9, 0)  # 9:00 AM predeterminado
                
                # Para end_time - usar valor predeterminado si no existe o es null
                end_time_str = entry.get('end_time')
                if end_time_str:
                    try:
                        end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
                    except (ValueError, TypeError):
                        end_time = datetime.time(17, 0)  # 5:00 PM predeterminado
                else:
                    end_time = datetime.time(17, 0)  # 5:00 PM predeterminado

                # Resto del código para usuario y UserProfile...
                user, created = User.objects.get_or_create(username=username, defaults={
                    'email': email,
                    'is_active': True
                })

                # Actualizar el usuario según sea necesario
                if created:
                    user.set_password(password)
                    resultados['creados'] += 1
                else:
                    if user.email != email:
                        user.email = email
                    if password:
                        user.set_password(password)
                    resultados['actualizados'] += 1

                user.save()

                # Crear o actualizar el perfil y worker
                profile, _ = UserProfile.objects.get_or_create(user=user)
                
                try:
                    worker = Worker.objects.get(user_profile=profile)
                    worker.dni = dni
                    worker.phone_number = phone
                    worker.start_date = start_date
                    worker.start_time = start_time
                    worker.end_time = end_time
                    worker.delete_date = None 
                except Worker.DoesNotExist:
                    worker = Worker(
                        user_profile=profile,
                        dni=dni,
                        phone_number=phone,
                        start_date=start_date,
                        start_time=start_time,
                        end_time=end_time
                    )
                
                # Guardar el worker
                worker.save()
                print(f"Worker guardado: {worker.dni}, fecha={worker.start_date}, inicio={worker.start_time}, fin={worker.end_time}")

            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"ERROR: {str(e)}\n{error_trace}")
                resultados['errores'].append({
                    'entry': entry,
                    'error': str(e),
                    'detail': error_trace[:500]
                })
                # Revert worker to its previous state if it exists in trabajadores_existentes
                for existing_worker in trabajadores_existentes:
                    if existing_worker['id'] == worker.id:
                        worker.dni = existing_worker['dni']
                        worker.phone_number = existing_worker['phone_number']
                        worker.start_date = existing_worker['start_date']
                        worker.start_time = existing_worker['start_time']
                        worker.end_time = existing_worker['end_time']
                        worker.delete_date = existing_worker['delete_date']
                        worker.save()
                        break
                else:
                    # If the worker was newly added, delete it
                    worker.delete()
        
        return JsonResponse(resultados)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def forgot_username(request):
    context = {}
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            
            # Generar una nueva contraseña temporal
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Actualizar la contraseña del usuario
            user.password = make_password(temp_password)
            user.save()
            
            # Enviar email con la información
            subject = 'Recuperación de datos de acceso'
            message = f'''
            Hola {user.first_name},
            
            Has solicitado la recuperación de tus datos de acceso.
            
            Tu nombre de usuario: {user.username}
            Tu contraseña temporal: {temp_password}
            
            Por favor, cambia tu contraseña tan pronto como inicies sesión.
            
            Saludos,
            El equipo de soporte
            '''
            
            from_email = 'noreply@tudominio.com'
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            context['success'] = 'Se ha enviado un correo electrónico con tus datos de acceso'
            
        except User.DoesNotExist:
            context['error'] = 'No existe ningún usuario con ese correo electrónico'
    
    return render(request, 'forgot_username.html', context)