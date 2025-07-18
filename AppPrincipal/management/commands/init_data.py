from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from AppPrincipal.models import PeriodoAcademico, Carpeta

class Command(BaseCommand):
    help = 'Inicializa datos de ejemplo para el sistema de gestión académica'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== INICIALIZANDO DATOS DE EJEMPLO ===\n'))
        
        try:
            # Crear períodos académicos
            self.crear_periodos_ejemplo()
            
            # Crear carpetas predefinidas para el período activo
            periodo_activo = PeriodoAcademico.objects.filter(activo=True).first()
            if periodo_activo:
                carpetas = self.crear_carpetas_predefinidas(periodo_activo)
                
                # Crear subcarpetas de ejemplo
                self.crear_subcarpetas_ejemplo(carpetas)
            
            self.stdout.write(self.style.SUCCESS('\n=== INICIALIZACIÓN COMPLETADA ==='))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error durante la inicialización: {e}'))

    def crear_periodos_ejemplo(self):
        """Crear períodos académicos de ejemplo"""
        self.stdout.write('Creando períodos académicos de ejemplo...')
        
        # Período 1 - 2024 (Activo)
        periodo1, created = PeriodoAcademico.objects.get_or_create(
            año=2024,
            periodo='1',
            defaults={
                'nombre': 'Primer Período 2024',
                'fecha_inicio': date(2024, 1, 15),
                'fecha_fin': date(2024, 6, 30),
                'activo': True,
                'descripcion': 'Primer período académico del año 2024'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Creado: {periodo1.nombre}')
        
        # Período 2 - 2024
        periodo2, created = PeriodoAcademico.objects.get_or_create(
            año=2024,
            periodo='2',
            defaults={
                'nombre': 'Segundo Período 2024',
                'fecha_inicio': date(2024, 7, 15),
                'fecha_fin': date(2024, 12, 15),
                'activo': False,
                'descripcion': 'Segundo período académico del año 2024'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Creado: {periodo2.nombre}')
        
        # Período 1 - 2023
        periodo3, created = PeriodoAcademico.objects.get_or_create(
            año=2023,
            periodo='1',
            defaults={
                'nombre': 'Primer Período 2023',
                'fecha_inicio': date(2023, 1, 15),
                'fecha_fin': date(2023, 6, 30),
                'activo': False,
                'descripcion': 'Primer período académico del año 2023'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Creado: {periodo3.nombre}')

    def crear_carpetas_predefinidas(self, periodo):
        """Crear las carpetas predefinidas para un período"""
        self.stdout.write(f'Creando carpetas predefinidas para {periodo.nombre}...')
        
        carpetas_predefinidas = [
            ('HORARIO GENERAL', 'Horarios generales del período', 1),
            ('CARGA HORARIA', 'Carga horaria de docentes', 2),
            ('MALLAS CURRICULARES', 'Mallas curriculares por carrera', 3),
            ('PEAS PARA REVISIÓN', 'PEAs pendientes de revisión', 4),
            ('PLANIFICACION ACADEMICA', 'Planificación académica del período', 5),
            ('INFORMACIÓN DE LA CARRERA', 'Información general de carreras', 6),
            ('PEA LEGALIZADOS', 'PEAs ya legalizados', 7),
            ('INFORMES ACADEMICOS', 'Informes académicos del período', 8),
            ('HORARIOS LEGALIZADOS', 'Horarios oficialmente aprobados', 9),
        ]
        
        carpetas_creadas = []
        admin_user = User.objects.filter(is_staff=True).first()
        
        for nombre, descripcion, orden in carpetas_predefinidas:
            carpeta, created = Carpeta.objects.get_or_create(
                nombre=nombre,
                periodo_academico=periodo,
                carpeta_padre=None,
                defaults={
                    'descripcion': descripcion,
                    'tipo_carpeta': 'predefinida',
                    'orden': orden,
                    'publica': False,
                    'usuario': admin_user
                }
            )
            if created:
                self.stdout.write(f'    ✓ Carpeta: {nombre}')
                carpetas_creadas.append(carpeta)
        
        return carpetas_creadas

    def crear_subcarpetas_ejemplo(self, carpetas):
        """Crear algunas subcarpetas de ejemplo"""
        subcarpetas_carreras = [
            'Ingeniería en Sistemas',
            'Administración de Empresas',
            'Contabilidad y Auditoría',
            'Derecho',
            'Psicología'
        ]
        
        # Buscar carpetas específicas para crear subcarpetas
        carpetas_con_subcarpetas = ['MALLAS CURRICULARES', 'INFORMACIÓN DE LA CARRERA']
        
        for carpeta in carpetas:
            if any(nombre in carpeta.nombre for nombre in carpetas_con_subcarpetas):
                self.stdout.write(f'  Creando subcarpetas para {carpeta.nombre}...')
                
                for i, nombre in enumerate(subcarpetas_carreras, 1):
                    subcarpeta, created = Carpeta.objects.get_or_create(
                        nombre=nombre,
                        carpeta_padre=carpeta,
                        periodo_academico=carpeta.periodo_academico,
                        defaults={
                            'descripcion': f'Subcarpeta para {nombre}',
                            'tipo_carpeta': 'subcarpeta',
                            'orden': i,
                            'publica': False,
                            'usuario': carpeta.usuario
                        }
                    )
                    if created:
                        self.stdout.write(f'      ✓ Subcarpeta: {nombre}')