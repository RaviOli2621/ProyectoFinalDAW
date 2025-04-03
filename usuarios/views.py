from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from usuarios.forms import CustomLoginForm, CustomSignInForm, WorkeCreaterForm, WorkerEditForm
from usuarios.models import Worker

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
        form = CustomLoginForm()  # Instancia vacía
        return render(request, "signin.html", {'form': form})

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
            return redirect("home")
    
# Admin users
@permission_required('auth.change_user')
def userList(request,user_id=""):
    if request.method == "GET":
        users = User.objects.all()

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
    workers = Worker.objects.all()

    return render(request, "admin/workerList.html",{
        "workers":workers
    })

@permission_required('auth.change_user')
def borrar_worker(request, worker_id):
    if request.method == 'POST':
        # Obtiene la reserva con el ID proporcionado, o devuelve un 404 si no existe.
        worker = get_object_or_404(Worker, id=worker_id)
        
        try:
            # Eliminar la reserva
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
        form = WorkeCreaterForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('workerList')  # Redirige a la lista de trabajadores
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
            # Pasar el worker y no es necesario pasar instance porque lo hacemos en __init__
            form = WorkerEditForm(request.POST, worker=worker)
            
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
