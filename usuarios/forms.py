from django import forms
from .models import Reserva, UserProfile, Worker  
from masajes.models import Masaje
from usuarios.models.user import UserManager  
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

class UserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
            })
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'})
    )
    foto = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1:
            if not password2:
                self.add_error('password2', 'Por favor, confirma la contraseña')
            elif password1 != password2:
                self.add_error('password2', 'Las contraseñas no coinciden')
                
        return cleaned_data

class TuModeloForm(forms.ModelForm):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('targeta', 'Tarjeta'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODOS_PAGO, required=True)

class Meta:
        model = Masaje 
        fields = ['fecha', 'duracion', 'metodo_pago']  

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'duracion', 'metodo_pago']
        widgets = {
            'duracion': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'duracion'):
            self.initial['duracion'] = self.instance.duracion
        elif 'initial' in kwargs and 'duracion' in kwargs['initial']:
            pass
        else:
            self.initial['duracion'] = 60
    
    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        
        if fecha:
            try:
                fecha_str = fecha.strftime('%Y-%m-%d')
                from django.urls import reverse
                from django.http import HttpRequest
                from masajes.views.calendar import horas_api  
                print(f"DEBUG - Consultando horas disponibles para: {fecha_str}")
                request = HttpRequest()
                request.method = 'GET'
                request.GET = {'fecha': fecha_str}
                from django.http import JsonResponse
                try:
                    response = horas_api(request)
                    if isinstance(response, JsonResponse):
                        horas_disponibles = response.content
                        import json
                        horas_disponibles = json.loads(horas_disponibles.decode('utf-8'))
                        fechaFormated = str(fecha).replace(' ', 'T')
                        hora_objeto = next((hora for hora in horas_disponibles if hora.get('fecha') == fechaFormated), None)
                        # Usar self.instance.fecha si existe, si no, None
                        reserva_fecha_actual = getattr(self.instance, 'fecha', None)
                        if not hora_objeto:
                            self.add_error('fecha', "No hay horas disponibles para esta fecha")
                        if hora_objeto["color"] == 'red' and reserva_fecha_actual != fecha:
                            self.add_error('fecha', "No hay horas disponibles para esta fecha")
                        self._horas_disponibles = horas_disponibles
                    else:
                        print(f"DEBUG - Respuesta inesperada de la API: {type(response)}")
                except Exception as e:
                    print(f"DEBUG - Error al llamar directamente a la vista: {e}")
            except Exception as e:
                import traceback
                print(f"DEBUG - Error al verificar disponibilidad: {type(e).__name__}: {e}")
                traceback.print_exc()
        return cleaned_data

class TarjetaForm(forms.Form):
    numero_tarjeta = forms.CharField(max_length=16, label="Número de tarjeta")
    fecha_expiracion = forms.CharField(max_length=5, label="Fecha de expiración (MM/YY)")
    cvv = forms.CharField(max_length=3, label="CVV")



class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})


class CustomSignInForm(UserCreationForm):
    gmail = forms.EmailField(
        required=True,  
        label="Gmail",
        widget=forms.EmailInput(attrs={ 'class': 'form-control'})
    )


class WorkeCreaterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    dni = forms.CharField(
        required=True,
        label="DNI",
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'})
    )
    
    phone_number = forms.CharField(
        required=True,
        label="Número de Teléfono",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )
    
    start_date = forms.DateField(
        required=True,
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    horario = forms.CharField(
        required=True,
        label="Horario de Trabajo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00 - 17:00'})
    )
    
    foto = forms.ImageField(
    required=False,
    label="Foto de Perfil",
    widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if UserManager.exists_with_username(username):
            raise forms.ValidationError("Ya existe un usuario con este nombre.")
        return username
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')

        if Worker.exists_with_dni(dni):
            raise forms.ValidationError("Ya existe un trabajador con este DNI.")
        return dni
    
    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if not horario:
            raise forms.ValidationError("Este campo es obligatorio")
        
        try:
            partes = horario.split('-')
            if len(partes) != 2:
                raise forms.ValidationError("El formato debe ser 'HH:MM - HH:MM'")
            
            start_time = partes[0].strip()
            end_time = partes[1].strip()
            
            import re
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):(30|00)$')
            
            if not time_pattern.match(start_time):
                raise forms.ValidationError(f"La hora de inicio '{start_time}' no tiene un formato válido (HH:MM)")
                
            if not time_pattern.match(end_time):
                raise forms.ValidationError(f"La hora de fin '{end_time}' no tiene un formato válido (HH:MM)")
            
    
            
            return {'start_time': start_time, 'end_time': end_time}
        except forms.ValidationError as e:
            raise e
        except Exception as e:
            raise forms.ValidationError(f"Error en el formato del horario: {str(e)}")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            user_profile, _ = UserProfile.get_or_create_by_user(user)

            if self.cleaned_data.get('foto'):
                user_profile.set_foto(self.cleaned_data['foto'])
            
            Worker.create_worker_from_form(user_profile, self.cleaned_data)
        
        return user
    
class WorkerEditForm(forms.Form):
    username = forms.CharField(
        required=True,
        label="Nombre de Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'})
    )
    
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    
    dni = forms.CharField(
        required=True,
        label="DNI",
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DNI'})
    )
    
    phone_number = forms.CharField(
        required=True,
        label="Número de Teléfono",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )
    
    start_date = forms.DateField(
        required=True,
        label="Fecha de Inicio",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    horario = forms.CharField(
        required=True,
        label="Horario de Trabajo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00 - 17:00'})
    )
    
    password1 = forms.CharField(
        required=False,
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        help_text="Dejar en blanco si no deseas cambiar la contraseña"
    )
    
    password2 = forms.CharField(
        required=False,
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    
    foto = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.worker_instance = kwargs.pop('worker', None)
        super().__init__(*args, **kwargs)
        
        if self.worker_instance:
            self.fields['username'].initial = self.worker_instance.user_profile.user.username
            self.fields['email'].initial = self.worker_instance.user_profile.user.email
            
            self.fields['dni'].initial = self.worker_instance.dni
            self.fields['phone_number'].initial = self.worker_instance.phone_number
            self.fields['start_date'].initial = self.worker_instance.start_date.strftime('%Y-%m-%d')
            self.fields['horario'].initial = f"{self.worker_instance.start_time.strftime('%H:%M')} - {self.worker_instance.end_time.strftime('%H:%M')}"
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if self.worker_instance:
            user_actual = self.worker_instance.user_profile.user

            if UserManager.exists_with_username(username, exclude_pk=user_actual.pk):
                raise forms.ValidationError("Ya existe un usuario con este nombre.")
        
        return username

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        
        if self.worker_instance:
            if Worker.exists_with_dni(dni, exclude_pk=self.worker_instance.pk):
                raise forms.ValidationError("Ya existe un trabajador con este DNI.")
        
        return dni
    
    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if not horario:
            raise forms.ValidationError("Este campo es obligatorio")
        
        try:
            partes = horario.split('-')
            if len(partes) != 2:
                raise forms.ValidationError("El formato debe ser 'HH:MM - HH:MM'")
            
            start_time = partes[0].strip()
            end_time = partes[1].strip()
            
            import re

            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):(30|00)$')
            
            if not time_pattern.match(start_time):
                raise forms.ValidationError(f"La hora de inicio '{start_time}' no tiene un formato válido (HH:MM)")
                
            if not time_pattern.match(end_time):
                raise forms.ValidationError(f"La hora de fin '{end_time}' no tiene un formato válido (HH:MM)")
            
            
            return {'start_time': start_time, 'end_time': end_time}
        except forms.ValidationError as e:
            raise e
        except Exception as e:
            raise forms.ValidationError(f"Error en el formato del horario: {str(e)}")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden")
            
        return cleaned_data
    
    def save(self, commit=True):
        if not self.worker_instance:
            raise ValueError("No se puede actualizar un trabajador sin proporcionar una instancia")
        
        user = self.worker_instance.user_profile.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        
        if self.cleaned_data.get('foto'):
            self.worker_instance.user_profile.foto = self.cleaned_data['foto']
        
        if commit:
            user.save()
            self.worker_instance.user_profile.save()

            self.worker_instance.update_worker_from_form(self.cleaned_data)
        
        return self.worker_instance