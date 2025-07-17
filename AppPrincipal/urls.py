from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('registro_admin/', views.registro_admin_view, name='registro_admin'),

    path('', views.dashboard, name='dashboard'),  # raíz apunta al dashboard (ajusta si quieres otra vista)

    # Usuarios (solo admin)
    path('crear_usuario/', views.crear_usuario, name='crear_usuario'),
    path('editar_usuario/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Carpetas
    path('crear_carpeta/', views.crear_carpeta, name='crear_carpeta'),
    path('editar_carpeta/<int:carpeta_id>/', views.editar_carpeta, name='editar_carpeta'),
    path('eliminar_carpeta/<int:carpeta_id>/', views.eliminar_carpeta, name='eliminar_carpeta'),

    # Archivos
    path('subir_archivo/<int:carpeta_id>/', views.subir_archivo, name='subir_archivo'),
    path('editar_archivo/<int:archivo_id>/', views.editar_archivo, name='editar_archivo'),
    path('eliminar_archivo/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),

    # Dashboard para usuario normal (opcional si quieres una URL distinta)
    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
]
