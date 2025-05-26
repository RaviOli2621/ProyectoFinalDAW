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
import jwt
from django.conf import settings

from usuarios.forms import CustomLoginForm, CustomSignInForm, UserEditForm, WorkeCreaterForm, WorkerEditForm
from usuarios.models import UserProfile, Worker
from usuarios.models.user import UserManager

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
                user = UserManager.create_user(
                    username=request.POST['username'],
                    email=request.POST['gmail'],
                    password=request.POST['password1']
                )
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
        form = CustomLoginForm()  
        if remembered_username:
            form.fields['username'].initial = remembered_username
        return render(request, "signin.html", {'form': form,'remembered_username': remembered_username if 'remembered_username' in locals() else ''})

    elif request.method == "POST":
        form = CustomLoginForm(data=request.POST)  

        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user is None:
            return render(request, "signin.html", {
                'form': form,  
                'toastTxt': "Usuario o contraseña incorrecta",
                "toastType": "error"
            })
        else: 
            login(request, user)
            if request.POST.get('remember_me', False):
                print(f"modongo")
                max_age = 30 * 24 * 60 * 60  
                response = redirect('home')  
                response.set_cookie('remembered_username', user.username, max_age=max_age)
                return response
            else:
                response = redirect('home')
                response.delete_cookie('remembered_username')
                return response    
@login_required
def editUser(request):
    if request.method == 'GET':
        user = request.user
        initial_data = {
            'username': user.username,
            'email': user.email,
        }
        form = UserEditForm(initial=initial_data)
        return render(request, "editUser.html", {
            "form": form,
        })
    elif request.method == 'POST':
        user = request.user
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user._original_email if hasattr(user, '_original_email') else UserManager.get_by_id(user.id).email
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
            user.save()
            if 'foto' in request.FILES:
                user_profile, _ = UserProfile.get_or_create_by_user(user)
                user_profile.set_foto(request.FILES['foto'])
                print(f"URL de la imagen guardada: {user_profile.foto.url}")
            if password1:
                login(request, user)
            return redirect('home')
        else:
            return render(request, "editUser.html", {
                "form": form,
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def userList(request, user_id=""):
    if request.method == "GET":
        users = Worker.get_users_without_pending_worker()
        return render(request, "admin/userList.html", {
            "usuarios": users
        })
    elif request.method == 'POST':
        user = UserManager.get_by_id(user_id)
        grupo = Group.objects.get(name="Administradores")
        if user.groups.filter(name="Administradores").exists():
            user.groups.remove(grupo)
            user.save()
            return JsonResponse({'success': True})
        else:
            user.groups.add(grupo)
            user.save()
            return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@permission_required('auth.change_user')
def workerList(request):
    workers = Worker.get_active_workers()
    return render(request, "admin/workerList.html", {
        "workers": workers
    })

@permission_required('auth.change_user')
def borrar_worker(request, worker_id):
    if request.method == 'POST':
        try:
            Worker.mark_for_deletion_by_id(worker_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def restore_worker(request):
    if request.method == 'POST':
        worker = Worker.restore_first_deleted_worker()
        if worker:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No hay trabajadores para restaurar'}, status=404)
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
        Worker.mark_all_active_as_deleted()
        for entry in data:
            try:
                username = entry.get('username')
                if not username:
                    raise ValueError("El campo 'username' es obligatorio")
                dni = entry.get('dni')
                if not dni:
                    raise ValueError("El campo 'dni' es obligatorio")
                phone = entry.get('phone_number', '')
                email = entry.get('email', '')
                password = entry.get('password', '')

                start_date_str = entry.get('start_date')
                if start_date_str:
                    try:
                        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        start_date = datetime.date.today()
                else:
                    start_date = datetime.date.today()

                start_time_str = entry.get('start_time')
                if start_time_str:
                    try:
                        start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
                    except ValueError:
                        start_time = datetime.time(9, 0)
                else:
                    start_time = datetime.time(9, 0)

                end_time_str = entry.get('end_time')
                if end_time_str:
                    try:
                        end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
                    except (ValueError, TypeError):
                        end_time = datetime.time(17, 0)
                else:
                    end_time = datetime.time(17, 0)

                user = UserManager.get_by_username(username)
                created = False
                if not user:
                    user = UserManager.create_user(username=username, email=email, password=password)
                    created = True
                    resultados['creados'] += 1
                else:
                    if user.email != email:
                        user.email = email
                    if password:
                        user.set_password(password)
                    resultados['actualizados'] += 1
                user.save()
                profile, _ = UserProfile.get_or_create_by_user(user)
                Worker.create_or_update_from_profile(
                    profile=profile,
                    dni=dni,
                    phone=phone,
                    start_date=start_date,
                    start_time=start_time,
                    end_time=end_time
                )
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                resultados['errores'].append({
                    'entry': entry,
                    'error': str(e),
                    'detail': error_trace[:500]
                })
        return JsonResponse(resultados)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def forgot_username(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            user = UserManager.get_by_email(email)
            if not user:
                raise User.DoesNotExist()
            profile, _ = UserProfile.get_or_create_by_user(user)
            payload = {
                'user_id': user.id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
                'jti': ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            profile.set_recover_token(token)
            reset_url = f"{request.build_absolute_uri('/')[:-1]}/recover-user?token={token}"
            subject = 'Recuperación de contraseña'
            message = f'''
            Hola {user.username},

            Has solicitado recuperar tu contraseña.
            Haz clic en el siguiente enlace para restablecerla (válido 1 hora, un solo uso):

            {reset_url}

            Si no solicitaste esto, ignora este correo.
            '''
            from_email = 'no-reply@tudominio.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            context['success'] = 'Se ha enviado un correo electrónico con el enlace para restablecer la contraseña'
        except User.DoesNotExist:
            context['error'] = 'No existe ningún usuario con ese correo electrónico'
    return render(request, 'forgot_username.html', context)

def recover_user(request):
    if( request.method == 'GET'):
        token = request.GET.get('token', '')
        if not token:
            return JsonResponse({'error': 'Token no proporcionado'}, status=400)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = UserManager.get_by_id(user_id)
            if not user:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            profile, _ = UserProfile.get_or_create_by_user(user)
            
            if profile.recover_token != token:
                return JsonResponse({'error': 'Token inválido o ya utilizado'}, status=400)

            initial_data = {
                'username': user.username,
                'email': user.email,
            }
            form = UserEditForm(initial=initial_data)
            return render(request, "editUser.html", {
                "form": form,
                'user': user,
                'token': token,
            })
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'El token ha expirado'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=400)
    elif request.method == 'POST':
        token = request.POST.get('token', '')
        if not token:
            return JsonResponse({'error': 'Token no proporcionado'}, status=400)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = UserManager.get_by_id(user_id)
            if not user:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            profile, _ = UserProfile.get_or_create_by_user(user)
            
            if profile.recover_token != token:
                return JsonResponse({'error': 'Token inválido o ya utilizado'}, status=400)

            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            if password1 != password2:
                return JsonResponse({'error': 'Las contraseñas no coinciden'}, status=400)

            user.set_password(password1)
            user.save()
            profile.set_recover_token(None)  
            login(request, user)  
            return redirect('home')
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'El token ha expirado'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=400)
    

@permission_required('auth.change_user')
def crear_worker(request):
    if request.method == 'GET':
        form = WorkeCreaterForm()
        return render(request, "admin/registerWorker.html", {
            "form": form,
        })
    elif request.method == 'POST':
        form = WorkeCreaterForm(request.POST, request.FILES)
        if form.is_valid():
            Worker.create_worker(form)
            return redirect('workerList')
        else:
            return render(request, "admin/registerWorker.html", {
                "form": form,
            })
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@permission_required('auth.change_user')
def editar_worker(request):
    if request.method == 'GET':
        trabajador_id = request.GET.get('trabajador_id')
        if trabajador_id:
            worker = get_object_or_404(Worker, id=trabajador_id)
            form = WorkerEditForm(worker=worker)
            return render(request, "admin/editWorker.html", {
                "form": form,
                "worker": worker,
            })
        else:
            return JsonResponse({'success': False, 'error': 'ID de trabajador no proporcionado'}, status=400)
    elif request.method == 'POST':
        trabajador_id = request.POST.get('trabajador_id')
        if trabajador_id:
            worker = get_object_or_404(Worker, id=trabajador_id)
            form = WorkerEditForm(request.POST, request.FILES, worker=worker)
            if form.is_valid():
                worker.update_worker(form)
                return redirect('workerList')
            else:
                return render(request, "admin/editWorker.html", {
                    "form": form,
                    "worker": worker,
                })
        else:
            return JsonResponse({'success': False, 'error': 'ID de trabajador no proporcionado'}, status=400)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)