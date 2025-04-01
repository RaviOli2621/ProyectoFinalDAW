from django import forms
from .models import Masaje, Reserva  # Importa tu modelo
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
