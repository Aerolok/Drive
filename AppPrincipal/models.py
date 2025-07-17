
from django.db import models
from django.contrib.auth.models import User

class Carpeta(models.Model):
    nombre = models.CharField(max_length=100, default='Archivo sin nombre')
    descripcion = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    publica = models.BooleanField(default=False)  # Nueva línea

    def __str__(self):
        return self.nombre
class Archivo(models.Model):
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='archivos', null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    archivo = models.FileField(upload_to='archivos/')
    nombre = models.CharField(max_length=200, default="Archivo sin nombre")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
