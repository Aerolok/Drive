from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from .forms import ArchivoForm, RegistroForm, CarpetaForm, PeriodoAcademicoForm, SubcarpetaForm, CarpetaEditForm, CarpetaCreateForm, ArchivoEditForm
from .models import Carpeta, Archivo, PeriodoAcademico
from django.contrib.auth.decorators import login_required
import zipfile
import os
from django.conf import settings
import tempfile
from django.contrib import messages

def is_admin(user):
    return user.is_staff

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'login.html')

def registro_admin_view(request):
    # Sólo se puede crear admin desde aquí
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True
            user.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro_admin.html', {'form': form})

@login_required
def editar_archivo(request, archivo_id):
    archivo = get_object_or_404(Archivo, id=archivo_id)
    
    # Verificar permisos
    if not request.user.is_staff and archivo.usuario != request.user:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method == 'POST':
        form = ArchivoEditForm(request.POST, request.FILES, instance=archivo)
        if form.is_valid():
            archivo_editado = form.save()
            return JsonResponse({
                'success': True, 
                'nuevo_nombre': archivo_editado.nombre
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ArchivoEditForm(instance=archivo)
        return render(request, 'modals/editar_archivo.html', {
            'form': form, 
            'archivo': archivo
        })

@login_required
def dashboard(request):
    if request.user.is_staff:
        # Para administradores, mostrar solo sus usuarios y períodos
        from .models import UsuarioAdministrador
        usuarios_creados = User.objects.filter(
            administradores_vinculados__administrador=request.user
        )
        periodos = PeriodoAcademico.objects.filter(administrador=request.user)
        periodo_activo = PeriodoAcademico.objects.filter(
            administrador=request.user, 
            activo=True
        ).first()
        
        # Filtrar carpetas por período activo del administrador
        if periodo_activo:
            carpetas = Carpeta.objects.filter(
                periodo_academico=periodo_activo
            ).prefetch_related('archivos', 'subcarpetas')
        else:
            carpetas = Carpeta.objects.none()
        
        # Estadísticas
        total_usuarios = usuarios_creados.count()
        total_carpetas = carpetas.count()
        total_archivos = Archivo.objects.filter(
            carpeta__periodo_academico__administrador=request.user
        ).count()
        
        context = {
            'usuarios': usuarios_creados,
            'carpetas': carpetas,
            'periodos': periodos,
            'periodo_activo': periodo_activo,
            'total_usuarios': total_usuarios,
            'total_carpetas': total_carpetas,
            'total_archivos': total_archivos,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        # Para usuarios normales, mostrar carpetas de todos los administradores que los agregaron
        from .models import UsuarioAdministrador
        
        # Obtener todos los administradores que agregaron a este usuario
        administradores = User.objects.filter(
            usuarios_creados__usuario=request.user
        )
        
        # Obtener todos los períodos activos de esos administradores
        periodos_activos = PeriodoAcademico.objects.filter(
            administrador__in=administradores,
            activo=True
        )
        
        # Obtener carpetas públicas de todos los períodos activos
        carpetas_publicas = Carpeta.objects.filter(
            publica=True,
            periodo_academico__in=periodos_activos
        ).prefetch_related('archivos', 'subcarpetas').order_by('periodo_academico__nombre', 'orden', 'nombre')
        
        # Archivos del usuario
        archivos = Archivo.objects.filter(usuario=request.user)
        
        context = {
            'carpetas': carpetas_publicas,
            'archivos': archivos,
            'periodos_activos': periodos_activos,
            'administradores': administradores,
        }
        return render(request, 'user_dashboard.html', context)

# ===== GESTIÓN DE PERÍODOS ACADÉMICOS =====

@login_required
@user_passes_test(is_admin)
def crear_periodo(request):
    if request.method == 'POST':
        form = PeriodoAcademicoForm(request.POST)
        if form.is_valid():
            periodo = form.save(commit=False)
            
            # Asignar el administrador que crea el período
            periodo.administrador = request.user
            
            # Si se marca como activo, desactivar otros períodos del mismo administrador
            if periodo.activo:
                PeriodoAcademico.objects.filter(
                    administrador=request.user,
                    activo=True
                ).update(activo=False)
            
            periodo.save()
            
            # Crear carpetas predefinidas para el nuevo período
            crear_carpetas_predefinidas(request.user, periodo)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = PeriodoAcademicoForm()
    return render(request, 'modals/crear_periodo.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_periodo(request, periodo_id):
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id, administrador=request.user)
    if request.method == 'POST':
        form = PeriodoAcademicoForm(request.POST, instance=periodo)
        if form.is_valid():
            periodo_editado = form.save(commit=False)
            
            # Si se marca como activo, desactivar otros períodos del mismo administrador
            if periodo_editado.activo:
                PeriodoAcademico.objects.filter(
                    administrador=request.user
                ).exclude(id=periodo_id).update(activo=False)
            
            periodo_editado.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = PeriodoAcademicoForm(instance=periodo)
    return render(request, 'modals/editar_periodo.html', {'form': form, 'periodo': periodo})

@login_required
@user_passes_test(is_admin)
def eliminar_periodo(request, periodo_id):
    if request.method == 'POST':
        periodo = get_object_or_404(PeriodoAcademico, id=periodo_id, administrador=request.user)
        periodo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
@user_passes_test(is_admin)
def activar_periodo(request, periodo_id):
    if request.method == 'POST':
        # Desactivar todos los períodos del administrador
        PeriodoAcademico.objects.filter(administrador=request.user).update(activo=False)
        
        # Activar el período seleccionado
        periodo = get_object_or_404(PeriodoAcademico, id=periodo_id, administrador=request.user)
        periodo.activo = True
        periodo.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def crear_carpetas_predefinidas(usuario, periodo):
    """Crea las carpetas predefinidas para un nuevo período académico"""
    carpetas_predefinidas = [
        ('horario_general', '1. HORARIO GENERAL', 'Horarios generales del período'),
        ('carga_horaria', '2. CARGA HORARIA', 'Carga horaria de docentes'),
        ('mallas_curriculares', '3. MALLAS CURRICULARES', 'Mallas curriculares actualizadas'),
        ('peas_revision', '4. PEAS PARA REVISIÓN', 'PEAs pendientes de revisión'),
        ('planificacion_academica', '5. PLANIFICACION ACADEMICA', 'Planificación académica del período'),
        ('informacion_carrera', '6. INFORMACIÓN DE LA CARRERA', 'Información general de la carrera'),
        ('pea_legalizados', '7. PEA LEGALIZADOS', 'PEAs ya legalizados'),
        ('informes_academicos', '8. INFORMES ACADEMICOS', 'Informes académicos del período'),
        ('horarios_legalizados', '9. HORARIOS LEGALIZADOS', 'Horarios legalizados'),
    ]
    
    for i, (tipo, nombre, descripcion) in enumerate(carpetas_predefinidas):
        Carpeta.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            usuario=usuario,
            periodo_academico=periodo,
            tipo_carpeta=tipo,
            orden=i + 1,
            publica=True
        )

# ===== GESTIÓN DE SUBCARPETAS =====

@login_required
def crear_subcarpeta(request, carpeta_padre_id):
    carpeta_padre = get_object_or_404(Carpeta, id=carpeta_padre_id)
    
    if request.method == 'POST':
        form = SubcarpetaForm(request.POST)
        if form.is_valid():
            subcarpeta = form.save(commit=False)
            subcarpeta.usuario = request.user
            subcarpeta.carpeta_padre = carpeta_padre
            subcarpeta.periodo_academico = carpeta_padre.periodo_academico
            subcarpeta.tipo_carpeta = 'personalizada'
            subcarpeta.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SubcarpetaForm()
    
    return render(request, 'modals/crear_subcarpeta.html', {
        'form': form, 
        'carpeta_padre': carpeta_padre
    })

# ===== EXPORTACIÓN A GOOGLE DRIVE =====

@login_required
@user_passes_test(is_admin)
def exportar_periodo_zip(request, periodo_id):
    """Exporta todas las carpetas de un período como archivo ZIP"""
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    
    # Crear un archivo ZIP temporal
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{periodo.nombre}_{periodo.año}.zip"'
    
    def agregar_carpeta_al_zip(zip_file, carpeta, ruta_base=""):
        """Función recursiva para agregar carpetas y subcarpetas al ZIP"""
        carpeta_path = f"{ruta_base}/{carpeta.nombre}" if ruta_base else carpeta.nombre
        
        # Agregar archivos de la carpeta actual
        archivos = Archivo.objects.filter(carpeta=carpeta)
        
        if not archivos.exists():
            # Crear carpeta vacía
            zip_file.writestr(f"{carpeta_path}/", "")
        else:
            for archivo in archivos:
                if archivo.archivo and os.path.exists(archivo.archivo.path):
                    archivo_path = f"{carpeta_path}/{archivo.nombre}"
                    zip_file.write(archivo.archivo.path, archivo_path)
        
        # Agregar subcarpetas recursivamente
        for subcarpeta in carpeta.subcarpetas.all():
            agregar_carpeta_al_zip(zip_file, subcarpeta, carpeta_path)
    
    with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Obtener todas las carpetas principales del período (sin carpeta_padre)
        carpetas_principales = Carpeta.objects.filter(
            periodo_academico=periodo, 
            carpeta_padre__isnull=True
        )
        
        for carpeta in carpetas_principales:
            agregar_carpeta_al_zip(zip_file, carpeta)
    
    return response

@login_required
@user_passes_test(is_admin)
def mostrar_opciones_exportacion(request, periodo_id):
    """Muestra las opciones de exportación (Local o Google Drive)"""
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    
    # Contar carpetas y archivos
    carpetas_principales = Carpeta.objects.filter(
        periodo_academico=periodo, 
        carpeta_padre__isnull=True
    )
    
    total_carpetas = 0
    total_archivos = 0
    
    def contar_recursivo(carpeta):
        nonlocal total_carpetas, total_archivos
        total_carpetas += 1
        total_archivos += carpeta.archivos.count()
        for subcarpeta in carpeta.subcarpetas.all():
            contar_recursivo(subcarpeta)
    
    for carpeta in carpetas_principales:
        contar_recursivo(carpeta)
    
    context = {
        'periodo': periodo,
        'total_carpetas': total_carpetas,
        'total_archivos': total_archivos,
        'carpetas_principales': carpetas_principales,
    }
    
    return render(request, 'modals/opciones_exportacion.html', context)

@login_required
@user_passes_test(is_admin)
def exportar_google_drive(request, periodo_id):
    """Exporta a Google Drive (simulación por ahora)"""
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    
    # Por ahora, simulamos la exportación a Google Drive
    # En una implementación real, aquí iría la integración con la API de Google Drive
    
    return JsonResponse({
        'success': True, 
        'message': f'Período "{periodo.nombre}" exportado exitosamente a Google Drive',
        'drive_url': 'https://drive.google.com/drive/folders/ejemplo'  # URL simulada
    })

@login_required
@user_passes_test(is_admin)
def preparar_exportacion_drive(request, periodo_id):
    """Prepara la exportación a Google Drive (interfaz)"""
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    carpetas = Carpeta.objects.filter(periodo_academico=periodo)
    
    context = {
        'periodo': periodo,
        'carpetas': carpetas,
        'total_archivos': sum(carpeta.archivos.count() for carpeta in carpetas),
    }
    
    return render(request, 'modals/exportar_drive.html', context)

# ===== VISTAS EXISTENTES ACTUALIZADAS =====

@login_required
@user_passes_test(is_admin)
def crear_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Crear la relación usuario-administrador
            from .models import UsuarioAdministrador
            UsuarioAdministrador.objects.create(
                usuario=user,
                administrador=request.user
            )
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegistroForm()
    return render(request, 'modals/crear_usuario.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegistroForm(instance=usuario)
    return render(request, 'modals/editar_usuario.html', {'form': form, 'usuario': usuario})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        if usuario != request.user:  # No permitir auto-eliminación
            usuario.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'No puedes eliminarte a ti mismo'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def crear_carpeta(request):
    if request.method == 'POST':
        form = CarpetaCreateForm(request.POST)
        if form.is_valid():
            carpeta = form.save(commit=False)
            carpeta.usuario = request.user
            
            if request.user.is_staff:
                # Para administradores, usar su período activo
                periodo_activo = PeriodoAcademico.objects.filter(
                    administrador=request.user,
                    activo=True
                ).first()
            else:
                # Para usuarios normales, obtener el primer período activo de sus administradores
                from .models import UsuarioAdministrador
                administradores = User.objects.filter(
                    usuarios_creados__usuario=request.user
                )
                periodo_activo = PeriodoAcademico.objects.filter(
                    administrador__in=administradores,
                    activo=True
                ).first()
            
            if periodo_activo:
                carpeta.periodo_academico = periodo_activo
            else:
                return JsonResponse({
                    'success': False, 
                    'errors': {'periodo': ['No hay período académico activo. Contacta al administrador.']}
                })
            
            carpeta.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Verificar que hay un período activo antes de mostrar el formulario
        if request.user.is_staff:
            periodo_activo = PeriodoAcademico.objects.filter(
                administrador=request.user,
                activo=True
            ).first()
        else:
            from .models import UsuarioAdministrador
            administradores = User.objects.filter(
                usuarios_creados__usuario=request.user
            )
            periodo_activo = PeriodoAcademico.objects.filter(
                administrador__in=administradores,
                activo=True
            ).first()
        
        if not periodo_activo:
            return JsonResponse({
                'success': False, 
                'error': 'No hay período académico activo'
            })
        
        form = CarpetaCreateForm()
        return render(request, 'modals/crear_carpeta.html', {
            'form': form,
            'periodo_activo': periodo_activo
        })

@login_required
def editar_carpeta(request, carpeta_id):
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    
    # Verificar permisos
    if not request.user.is_staff and carpeta.usuario != request.user:
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    if request.method == 'POST':
        form = CarpetaEditForm(request.POST, instance=carpeta)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CarpetaEditForm(instance=carpeta)
    return render(request, 'modals/editar_carpeta.html', {'form': form, 'carpeta': carpeta})

@login_required
def eliminar_carpeta(request, carpeta_id):
    if request.method == 'POST':
        carpeta = get_object_or_404(Carpeta, id=carpeta_id)
        
        # Verificar permisos
        if not request.user.is_staff and carpeta.usuario != request.user:
            return JsonResponse({'success': False, 'error': 'Sin permisos'})
        
        carpeta.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def subir_archivo(request, carpeta_id=None):
    carpeta = None
    if carpeta_id:
        carpeta = get_object_or_404(Carpeta, id=carpeta_id)
        # Verificar que la carpeta pertenece a un período activo del usuario
        if request.user.is_staff:
            periodos_activos = PeriodoAcademico.objects.filter(
                administrador=request.user,
                activo=True
            )
        else:
            from .models import UsuarioAdministrador
            administradores = User.objects.filter(
                usuarios_creados__usuario=request.user
            )
            periodos_activos = PeriodoAcademico.objects.filter(
                administrador__in=administradores,
                activo=True
            )
        
        if not periodos_activos.filter(id=carpeta.periodo_academico.id).exists():
            return JsonResponse({
                'success': False, 
                'error': 'La carpeta no pertenece a un período académico activo'
            })
    
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.usuario = request.user
            if carpeta:
                archivo.carpeta = carpeta
            archivo.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        # Obtener períodos activos según el tipo de usuario
        if request.user.is_staff:
            periodos_activos = PeriodoAcademico.objects.filter(
                administrador=request.user,
                activo=True
            )
        else:
            from .models import UsuarioAdministrador
            administradores = User.objects.filter(
                usuarios_creados__usuario=request.user
            )
            periodos_activos = PeriodoAcademico.objects.filter(
                administrador__in=administradores,
                activo=True
            )
        
        if not periodos_activos.exists():
            return JsonResponse({
                'success': False, 
                'error': 'No hay período académico activo'
            })
        
        # Filtrar carpetas públicas de los períodos activos
        carpetas_disponibles = Carpeta.objects.filter(
            periodo_academico__in=periodos_activos,
            publica=True
        ).order_by('periodo_academico__nombre', 'nombre')
        
        form = ArchivoForm()
        # Actualizar las opciones del campo carpeta
        form.fields['carpeta'].queryset = carpetas_disponibles
        form.fields['carpeta'].required = True
        
        return render(request, 'modals/subir_archivo.html', {
            'form': form, 
            'carpeta': carpeta,
            'periodos_activos': periodos_activos,
            'carpetas_disponibles': carpetas_disponibles
        })

@login_required
def eliminar_archivo(request, archivo_id):
    if request.method == 'POST':
        archivo = get_object_or_404(Archivo, id=archivo_id)
        
        # Verificar permisos
        if not request.user.is_staff and archivo.usuario != request.user:
            return JsonResponse({'success': False, 'error': 'Sin permisos'})
        
        # Eliminar archivo físico
        if archivo.archivo and os.path.exists(archivo.archivo.path):
            os.remove(archivo.archivo.path)
        
        archivo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def logout_view(request):
    logout(request)
    return redirect('login')



