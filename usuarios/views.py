from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

# Create your views here.

def signup(request):
    if request.method == "GET": 
        return render(request,'signup.html',{
            'form':UserCreationForm,
        })    
    elif request.method == "POST": 
        if(request.POST['password2'] == request.POST['password1']):
            errorText = ""
            try:
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect("home")
            except IntegrityError:
                errorText = "User alredy exist"
        else: errorText = "The passwords does not match"
        return render(request,'signup.html',{
            'form':UserCreationForm,
            'error':errorText
        })  

@login_required
def signout(request):
    logout(request)
    return redirect("home")

def signin(request):
    if request.method == "GET": 
        return render(request,"signin.html", {
            'form':AuthenticationForm
        })
    elif request.method == "POST":
        print(request.POST)
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,"signin.html", {
                'form':AuthenticationForm,
                'error':"Username/Password is incorrect"
            })
        else: 
            login(request,user)
            return redirect("home")
        
