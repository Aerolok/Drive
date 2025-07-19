from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro_admin/', views.registro_admin_view, name='registro_admin'),
    path('', views.dashboard, name='dashboard'),

    # ===== GESTIÓN DE USUARIOS (solo admin) =====
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('editar_usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # ===== GESTIÓN DE PERÍODOS ACADÉMICOS =====
    path('crear_periodo/', views.crear_periodo, name='crear_periodo'),
    path('editar_periodo/<int:periodo_id>/', views.editar_periodo, name='editar_periodo'),
    path('eliminar_periodo/<int:periodo_id>/', views.eliminar_periodo, name='eliminar_periodo'),
    path('activar_periodo/<int:periodo_id>/', views.activar_periodo, name='activar_periodo'),

    # ===== GESTIÓN DE CARPETAS =====
    path('crear_carpeta/', views.crear_carpeta, name='crear_carpeta'),
    path('editar_carpeta/<int:carpeta_id>/', views.editar_carpeta, name='editar_carpeta'),
    path('eliminar_carpeta/<int:carpeta_id>/', views.eliminar_carpeta, name='eliminar_carpeta'),
    path('descargar_carpeta/<int:carpeta_id>/', views.descargar_carpeta, name='descargar_carpeta'),
    path('obtener_archivos_carpeta/<int:carpeta_id>/', views.obtener_archivos_carpeta, name='obtener_archivos_carpeta'),

    # ===== GESTIÓN DE SUBCARPETAS =====
    path('crear_subcarpeta/<int:carpeta_padre_id>/', views.crear_subcarpeta, name='crear_subcarpeta'),

    # ===== API ENDPOINTS =====
    path('api/carpetas/', views.api_carpetas, name='api_carpetas'),
    
    # ===== GESTIÓN DE ARCHIVOS =====
    path('subir_archivo/', views.subir_archivo, name='subir_archivo'),
    path('subir_archivo/<int:carpeta_id>/', views.subir_archivo, name='subir_archivo_carpeta'),
    path('editar_archivo/<int:archivo_id>/', views.editar_archivo, name='editar_archivo'),
    path('eliminar_archivo/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path('descargar_archivo/<int:archivo_id>/', views.descargar_archivo, name='descargar_archivo'),

    # ===== EXPORTACIÓN =====
    path('opciones_exportacion/<int:periodo_id>/', views.mostrar_opciones_exportacion, name='opciones_exportacion'),
    path('exportar_periodo_zip/<int:periodo_id>/', views.exportar_periodo_zip, name='exportar_periodo_zip'),
    path('exportar_google_drive/<int:periodo_id>/', views.exportar_google_drive, name='exportar_google_drive'),
    path('preparar_exportacion_drive/<int:periodo_id>/', views.preparar_exportacion_drive, name='preparar_exportacion_drive'),
]
