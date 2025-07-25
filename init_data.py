#!/usr/bin/env python
"""
Script para inicializar datos de ejemplo en el sistema
"""
import os
import sys
import django
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miapp.settings')
django.setup()

from AppPrincipal.models import PeriodoAcademico, Carpeta
from django.contrib.auth.models import User

def crear_periodos_ejemplo():
    """Crear períodos académicos de ejemplo"""
    print("Creando períodos académicos de ejemplo...")
    
    # Período 1 - 2024 (Activo)
    periodo1, created = PeriodoAcademico.objects.get_or_create(
        año=2024,
        periodo=1,
        defaults={
            'nombre': 'Primer Período 2024',
            'fecha_inicio': date(2024, 1, 15),
            'fecha_fin': date(2024, 6, 30),
            'activo': True,
            'descripcion': 'Primer período académico del año 2024'
        }
    )
    if created:
        print(f"✓ Creado: {periodo1.nombre}")
    
    # Período 2 - 2024
    periodo2, created = PeriodoAcademico.objects.get_or_create(
        año=2024,
        periodo=2,
        defaults={
            'nombre': 'Segundo Período 2024',
            'fecha_inicio': date(2024, 7, 15),
            'fecha_fin': date(2024, 12, 15),
            'activo': False,
            'descripcion': 'Segundo período académico del año 2024'
        }
    )
    if created:
        print(f"✓ Creado: {periodo2.nombre}")
    
    # Período 1 - 2023
    periodo3, created = PeriodoAcademico.objects.get_or_create(
        año=2023,
        periodo=1,
        defaults={
            'nombre': 'Primer Período 2023',
            'fecha_inicio': date(2023, 1, 15),
            'fecha_fin': date(2023, 6, 30),
            'activo': False,
            'descripcion': 'Primer período académico del año 2023'
        }
    )
    if created:
        print(f"✓ Creado: {periodo3.nombre}")
    
    return periodo1, periodo2, periodo3

def crear_carpetas_predefinidas(periodo):
    """Crear las carpetas predefinidas para un período"""
    print(f"Creando carpetas predefinidas para {periodo.nombre}...")
    
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
    for nombre, descripcion, orden in carpetas_predefinidas:
        carpeta, created = Carpeta.objects.get_or_create(
            nombre=nombre,
            periodo_academico=periodo,
            carpeta_padre=None,
            defaults={
                'descripcion': descripcion,
                'tipo_carpeta': 'personalizada',
                'orden': orden,
                'publica': False,
                'usuario': User.objects.filter(is_staff=True).first()
            }
        )
        if created:
            print(f"  ✓ Carpeta: {nombre}")
            carpetas_creadas.append(carpeta)
    
    return carpetas_creadas

def crear_subcarpetas_ejemplo(carpeta_padre):
    """Crear algunas subcarpetas de ejemplo"""
    subcarpetas = [
        'Ingeniería en Sistemas',
        'Administración de Empresas',
        'Contabilidad y Auditoría',
        'Derecho',
        'Psicología'
    ]
    
    for i, nombre in enumerate(subcarpetas, 1):
        subcarpeta, created = Carpeta.objects.get_or_create(
            nombre=nombre,
            carpeta_padre=carpeta_padre,
            periodo_academico=carpeta_padre.periodo_academico,
            defaults={
                'descripcion': f'Subcarpeta para {nombre}',
                'tipo_carpeta': 'personalizada',
                'orden': i,
                'publica': False,
                'usuario': carpeta_padre.usuario
            }
        )
        if created:
            print(f"    ✓ Subcarpeta: {nombre}")

def main():
    """Función principal"""
    print("=== INICIALIZANDO DATOS DE EJEMPLO ===\n")
    
    try:
        # Crear períodos académicos
        periodo1, periodo2, periodo3 = crear_periodos_ejemplo()
        
        # Crear carpetas predefinidas para el período activo
        carpetas = crear_carpetas_predefinidas(periodo1)
        
        # Crear subcarpetas de ejemplo para algunas carpetas
        if carpetas:
            # Crear subcarpetas para "MALLAS CURRICULARES"
            mallas_carpeta = next((c for c in carpetas if 'MALLAS' in c.nombre), None)
            if mallas_carpeta:
                print(f"Creando subcarpetas para {mallas_carpeta.nombre}...")
                crear_subcarpetas_ejemplo(mallas_carpeta)
            
            # Crear subcarpetas para "INFORMACIÓN DE LA CARRERA"
            info_carpeta = next((c for c in carpetas if 'INFORMACIÓN' in c.nombre), None)
            if info_carpeta:
                print(f"Creando subcarpetas para {info_carpeta.nombre}...")
                crear_subcarpetas_ejemplo(info_carpeta)
        
        print("\n=== INICIALIZACIÓN COMPLETADA ===")
        print(f"✓ Períodos académicos creados: 3")
        print(f"✓ Carpetas predefinidas creadas: {len(carpetas)}")
        print(f"✓ Período activo: {periodo1.nombre}")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()