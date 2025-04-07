from django import forms
from .models import Masaje, Reserva, UserProfile, Worker  # Importa tu modelo
from django.contrib.auth.models import User  # Importa el modelo User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm


class TuModeloForm(forms.ModelForm):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('targeta', 'Tarjeta'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODOS_PAGO, required=True)

class Meta:
        model = Masaje  # Aquí se asocia el modelo Masaje
        fields = ['fecha', 'duracion', 'metodo_pago']  # Campos que quieres incluir en el formulario

# Formulario para la creación de una reserva
class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha', 'duracion', 'metodo_pago']

class TarjetaForm(forms.Form):
    numero_tarjeta = forms.CharField(max_length=16, label="Número de tarjeta")
    fecha_expiracion = forms.CharField(max_length=5, label="Fecha de expiración (MM/YY)")
    cvv = forms.CharField(max_length=3, label="CVV")

# LOGIN Y SIGNUP


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})


class CustomSignInForm(UserCreationForm):
    gmail = forms.EmailField(
        required=True,  # No obligatorio si solo es informativo
        label="Gmail",
        widget=forms.EmailInput(attrs={ 'class': 'form-control'})
    )

# Formulario para trabajador

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
        # Aplicar estilos a los campos
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ya existe un usuario con este nombre.")
        return username
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if Worker.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un trabajador con este DNI.")
        return dni
    
    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if not horario:
            raise forms.ValidationError("Este campo es obligatorio")
        
        try:
            # Dividir el horario en inicio y fin
            partes = horario.split('-')
            if len(partes) != 2:
                raise forms.ValidationError("El formato debe ser 'HH:MM - HH:MM'")
            
            start_time = partes[0].strip()
            end_time = partes[1].strip()
            
            # Validar formato de hora (HH:MM)
            import re
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):(30|00)$')
            
            if not time_pattern.match(start_time):
                raise forms.ValidationError(f"La hora de inicio '{start_time}' no tiene un formato válido (HH:MM)")
                
            if not time_pattern.match(end_time):
                raise forms.ValidationError(f"La hora de fin '{end_time}' no tiene un formato válido (HH:MM)")
            
            # Podríamos añadir más validaciones si quisiéramos (por ejemplo, que end_time > start_time)
            
            return {'start_time': start_time, 'end_time': end_time}
        except forms.ValidationError as e:
            # Re-lanzamos excepciones de validación específicas
            raise e
        except Exception as e:
            # Para otros errores, mostramos un mensaje más detallado
            raise forms.ValidationError(f"Error en el formato del horario: {str(e)}")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            user_profile = UserProfile.objects.get_or_create(user=user)[0]

            #Si hay foto, la guardamos
            if self.cleaned_data.get('foto'):
                user_profile.foto = self.cleaned_data['foto']
                user_profile.save()
            
            horario = self.cleaned_data.get('horario')
            worker = Worker.objects.create(
                user_profile=user_profile,
                dni=self.cleaned_data['dni'],
                phone_number=self.cleaned_data['phone_number'],
                start_date=self.cleaned_data['start_date'],
                start_time=horario['start_time'],
                end_time=horario['end_time']
            )
        
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
    
    # (opcionales)
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
        # Extraer el worker para inicializar campos
        self.worker_instance = kwargs.pop('worker', None)
        super().__init__(*args, **kwargs)
        
        # Si tenemos una instancia de worker, inicializar los campos
        if self.worker_instance:
            # Inicializar campos del User
            self.fields['username'].initial = self.worker_instance.user_profile.user.username
            self.fields['email'].initial = self.worker_instance.user_profile.user.email
            
            # Inicializar campos del Worker (no UserProfile)
            self.fields['dni'].initial = self.worker_instance.dni
            self.fields['phone_number'].initial = self.worker_instance.phone_number
            self.fields['start_date'].initial = self.worker_instance.start_date.strftime('%Y-%m-%d')
            self.fields['horario'].initial = f"{self.worker_instance.start_time.strftime('%H:%M')} - {self.worker_instance.end_time.strftime('%H:%M')}"
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Si tenemos una instancia, verificamos que no haya otro usuario con este nombre
        if self.worker_instance:
            # Excluimos al usuario actual de la validación de unicidad
            user_actual = self.worker_instance.user_profile.user
            if User.objects.filter(username=username).exclude(pk=user_actual.pk).exists():
                raise forms.ValidationError("Ya existe un usuario con este nombre.")
        
        return username

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        
        # Si tenemos una instancia, verificamos que no haya otro worker con este DNI
        if self.worker_instance:
            if Worker.objects.filter(dni=dni).exclude(pk=self.worker_instance.pk).exists():
                raise forms.ValidationError("Ya existe un trabajador con este DNI.")
        
        return dni
    
    def clean_horario(self):
        horario = self.cleaned_data.get('horario')
        if not horario:
            raise forms.ValidationError("Este campo es obligatorio")
        
        try:
            # Dividir el horario en inicio y fin
            partes = horario.split('-')
            if len(partes) != 2:
                raise forms.ValidationError("El formato debe ser 'HH:MM - HH:MM'")
            
            start_time = partes[0].strip()
            end_time = partes[1].strip()
            
            # Validar formato de hora (HH:MM)
            import re
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):(30|00)$')
            
            if not time_pattern.match(start_time):
                raise forms.ValidationError(f"La hora de inicio '{start_time}' no tiene un formato válido (HH:MM)")
                
            if not time_pattern.match(end_time):
                raise forms.ValidationError(f"La hora de fin '{end_time}' no tiene un formato válido (HH:MM)")
            
            # Podríamos añadir más validaciones si quisiéramos (por ejemplo, que end_time > start_time)
            
            return {'start_time': start_time, 'end_time': end_time}
        except forms.ValidationError as e:
            # Re-lanzamos excepciones de validación específicas
            raise e
        except Exception as e:
            # Para otros errores, mostramos un mensaje más detallado
            raise forms.ValidationError(f"Error en el formato del horario: {str(e)}")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Validar que las contraseñas coincidan (solo si se ha proporcionado al menos una)
        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden")
            
        return cleaned_data
    
    def save(self, commit=True):
        if not self.worker_instance:
            raise ValueError("No se puede actualizar un trabajador sin proporcionar una instancia")
        
        # Actualizar User
        user = self.worker_instance.user_profile.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        
        # Cambiar la contraseña si se proporcionó una nueva
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        
        # Actualizar Worker directamente
        worker = self.worker_instance
        worker.dni = self.cleaned_data['dni']
        worker.phone_number = self.cleaned_data['phone_number']
        worker.start_date = self.cleaned_data['start_date']
        
        horario = self.cleaned_data.get('horario')
        worker.start_time = horario['start_time']
        worker.end_time = horario['end_time']
        
        # Actualizar foto si se proporcionó una nueva
        if self.cleaned_data.get('foto'):
            worker.user_profile.foto = self.cleaned_data['foto']
        
        if commit:
            user.save()
            worker.user_profile.save()  # Guardar el perfil para la foto
            worker.save()
        
        return worker