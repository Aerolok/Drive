
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PeriodoAcademico(models.Model):
    PERIODOS_CHOICES = [
        ('1', 'Período 1'),
        ('2', 'Período 2'),
    ]
    
    nombre = models.CharField(max_length=50)
    periodo = models.CharField(max_length=1, choices=PERIODOS_CHOICES)
    año = models.IntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='periodos_creados', null=True, blank=True)
    
    class Meta:
        unique_together = ['periodo', 'año', 'administrador']
        ordering = ['-año', '-periodo']
    
    def __str__(self):
        return f"{self.nombre} - {self.año} ({self.administrador.username})"

class UsuarioAdministrador(models.Model):
    """Modelo para vincular usuarios con los administradores que los crearon"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administradores_vinculados')
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usuarios_creados')
    fecha_vinculacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['usuario', 'administrador']
    
    def __str__(self):
        return f"{self.usuario.username} creado por {self.administrador.username}"

class Carpeta(models.Model):
    TIPOS_CARPETA = [
        ('horario_general', '1. HORARIO GENERAL'),
        ('carga_horaria', '2. CARGA HORARIA'),
        ('mallas_curriculares', '3. MALLAS CURRICULARES'),
        ('peas_revision', '4. PEAS PARA REVISIÓN'),
        ('planificacion_academica', '5. PLANIFICACION ACADEMICA'),
        ('informacion_carrera', '6. INFORMACIÓN DE LA CARRERA'),
        ('pea_legalizados', '7. PEA LEGALIZADOS'),
        ('informes_academicos', '8. INFORMES ACADEMICOS'),
        ('horarios_legalizados', '9. HORARIOS LEGALIZADOS'),
        ('personalizada', 'Carpeta Personalizada'),
    ]
    
    nombre = models.CharField(max_length=100, default='Archivo sin nombre')
    descripcion = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    publica = models.BooleanField(default=False)
    periodo_academico = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE, null=True, blank=True)
    carpeta_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcarpetas')
    tipo_carpeta = models.CharField(max_length=30, choices=TIPOS_CARPETA, default='personalizada')
    orden = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        if self.carpeta_padre:
            return f"{self.carpeta_padre.nombre} > {self.nombre}"
        return self.nombre
    
    def get_ruta_completa(self):
        """Obtiene la ruta completa de la carpeta incluyendo subcarpetas"""
        if self.carpeta_padre:
            return f"{self.carpeta_padre.get_ruta_completa()} > {self.nombre}"
        return self.nombre
        
class Archivo(models.Model):
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='archivos', null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    archivo = models.FileField(upload_to='archivos/')
    nombre = models.CharField(max_length=200, default="Archivo sin nombre")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
