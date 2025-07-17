from django import forms
from django.contrib.auth.models import User
from .models import Carpeta
from .models import Archivo

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    is_staff = forms.BooleanField(label="¿Administrador?", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_staff']

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if not pwd:
            raise forms.ValidationError("La contraseña es obligatoria")
        return pwd

class CarpetaForm(forms.ModelForm):
    publica = forms.BooleanField(label="¿Visible para todos los usuarios?", required=False)

    class Meta:
        model = Carpeta
        fields = ['nombre', 'descripcion', 'publica']  # Añadimos 'publica'

class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['nombre', 'archivo', 'carpeta']
