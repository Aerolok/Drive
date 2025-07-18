from django import forms
from django.contrib.auth.models import User
from .models import Carpeta, Archivo, PeriodoAcademico

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

class PeriodoAcademicoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcademico
        fields = ['nombre', 'periodo', 'año', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Primer Semestre 2024'}),
        }

class CarpetaForm(forms.ModelForm):
    publica = forms.BooleanField(label="¿Visible para todos los usuarios?", required=False)

    class Meta:
        model = Carpeta
        fields = ['nombre', 'descripcion', 'publica', 'periodo_academico', 'carpeta_padre', 'tipo_carpeta']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar períodos académicos activos
        self.fields['periodo_academico'].queryset = PeriodoAcademico.objects.filter(activo=True)
        self.fields['periodo_academico'].required = False
        
        # Filtrar carpetas padre (solo carpetas principales, no subcarpetas)
        if user:
            self.fields['carpeta_padre'].queryset = Carpeta.objects.filter(
                usuario=user, 
                carpeta_padre__isnull=True
            )
        self.fields['carpeta_padre'].required = False

class CarpetaEditForm(forms.ModelForm):
    """Formulario simplificado para editar carpetas"""
    publica = forms.BooleanField(label="¿Visible para todos los usuarios?", required=False)

    class Meta:
        model = Carpeta
        fields = ['nombre', 'descripcion', 'publica']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción de la carpeta...'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la carpeta'}),
        }

class CarpetaCreateForm(forms.ModelForm):
    """Formulario para crear carpetas con más flexibilidad"""
    publica = forms.BooleanField(label="¿Visible para todos los usuarios?", required=False, initial=True)

    class Meta:
        model = Carpeta
        fields = ['nombre', 'descripcion', 'publica']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción de la carpeta...'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la carpeta'}),
        }

class SubcarpetaForm(forms.ModelForm):
    class Meta:
        model = Carpeta
        fields = ['nombre', 'descripcion', 'publica']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class ArchivoForm(forms.ModelForm):
    class Meta:
        model = Archivo
        fields = ['nombre', 'archivo', 'carpeta']

class ArchivoEditForm(forms.ModelForm):
    """Formulario para editar archivos (solo nombre y descripción)"""
    class Meta:
        model = Archivo
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del archivo'}),
        }
