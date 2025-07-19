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

class EditarUsuarioForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Nueva contraseña (opcional)")
    is_staff = forms.BooleanField(label="¿Administrador?", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("El nombre de usuario es obligatorio")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("El email es obligatorio")
        return email

class PeriodoAcademicoForm(forms.ModelForm):
    class Meta:
        model = PeriodoAcademico
        fields = ['nombre', 'periodo', 'año', 'fecha_inicio', 'fecha_fin', 'descripcion', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Primer Semestre 2024'}),
            'año': forms.NumberInput(attrs={'placeholder': '2024'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos opcionales
        self.fields['fecha_inicio'].required = False
        self.fields['fecha_fin'].required = False
        self.fields['descripcion'].required = False
        self.fields['activo'].required = False
        
        # Establecer año actual por defecto
        from datetime import datetime
        if not self.instance.pk:  # Solo para nuevos períodos
            self.fields['año'].initial = datetime.now().year
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        año = cleaned_data.get('año')
        
        if periodo and año:
            # Verificar si ya existe un período con la misma combinación
            existing = PeriodoAcademico.objects.filter(
                periodo=periodo,
                año=año
            )
            
            # Si estamos editando, excluir el período actual
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    f'Ya existe un período "{periodo}" para el año {año}. '
                    'Por favor, elige una combinación diferente.'
                )
        
        return cleaned_data

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
