from django import forms
from .models import Masaje, Reserva  # Importa tu modelo


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