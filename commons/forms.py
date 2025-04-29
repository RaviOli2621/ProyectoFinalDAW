from django import forms

class EnviarCorreoForm(forms.Form):
    correo_usuario = forms.EmailField(label='Tu correo')
    titulo = forms.CharField(max_length=30, label='Titulo')
    asunto = forms.CharField(max_length=100, label='Asunto')
    cuerpo = forms.CharField(widget=forms.Textarea, label='Cuerpo del mensaje')