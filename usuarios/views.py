from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from usuarios.forms import CustomLoginForm, CustomSignInForm

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
            'form':authentication_form,
            "toastTxt": " ",
            "toastType": "error"
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
                errorText = "User already exists"
        else: errorText = "The passwords do not match"
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
                'toastTxt': "Username/Password is incorrect",
                "toastType": "error"
            })
        else: 
            login(request, user)
            return redirect("home")
    
@permission_required('auth.change_user')
def userList(request):
    users = User.objects.all()

    return render(request, "admin/userList.html",{
        "usuarios":users
    })

@permission_required('auth.change_user')
def cambiar_privilegios(request,user_id):
    if request.method == 'POST':
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