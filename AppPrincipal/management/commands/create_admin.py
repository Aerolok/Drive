from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea un superusuario administrador por defecto'

    def handle(self, *args, **options):
        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Ya existe un superusuario en el sistema.')
            )
            return

        # Crear superusuario por defecto
        User.objects.create_superuser(
            username='admin',
            email='admin@drive.com',
            password='admin123'
        )
        
        self.stdout.write(
            self.style.SUCCESS('Superusuario creado exitosamente:')
        )
        self.stdout.write(f'  Usuario: admin')
        self.stdout.write(f'  Contraseña: admin123')
        self.stdout.write(f'  Email: admin@drive.com')
        self.stdout.write(
            self.style.WARNING('¡IMPORTANTE: Cambia la contraseña después del primer login!')
        )