from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import ArchivoForm, RegistroForm, CarpetaForm
from .models import Carpeta
from AppPrincipal import models
from django.contrib.auth.decorators import login_required
from .models import Carpeta, Archivo

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
def dashboard(request):
    if request.user.is_staff:
        usuarios = User.objects.all()
        carpetas = Carpeta.objects.all().prefetch_related('archivos')
        return render(request, 'admin_dashboard.html', {'usuarios': usuarios, 'carpetas': carpetas})
    else:
        carpetas_propias = Carpeta.objects.filter(usuario=request.user)
        carpetas_publicas = Carpeta.objects.filter(publica=True)
        carpetas = (carpetas_propias | carpetas_publicas).distinct()
        archivos = Archivo.objects.filter(usuario=request.user)
        return render(request, 'user_dashboard.html', {'carpetas': carpetas, 'archivos': archivos})





@login_required
@user_passes_test(is_admin)
def crear_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegistroForm()
    return render(request, 'modals/crear_usuario.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save(commit=False)
            pwd = form.cleaned_data['password']
            if pwd:
                user.set_password(pwd)
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RegistroForm(instance=user_obj)
        form.fields['password'].required = False
        form.initial['password'] = ''
    return render(request, 'modals/editar_usuario.html', {'form': form, 'user_obj': user_obj})

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        user_obj.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def crear_carpeta(request):
    if request.method == 'POST':
        form = CarpetaForm(request.POST)
        if form.is_valid():
            carpeta = form.save(commit=False)
            carpeta.usuario = request.user
            carpeta.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CarpetaForm()
    return render(request, 'modals/crear_carpeta.html', {'form': form})

@login_required
def editar_carpeta(request, carpeta_id):
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)
    if request.method == 'POST':
        form = CarpetaForm(request.POST, instance=carpeta)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CarpetaForm(instance=carpeta)
    return render(request, 'modals/editar_carpeta.html', {'form': form, 'carpeta': carpeta})

@login_required
def eliminar_carpeta(request, carpeta_id):
    if request.method == 'POST':
        carpeta = get_object_or_404(Carpeta, id=carpeta_id)
        carpeta.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def subir_archivo(request, carpeta_id):
    carpeta = get_object_or_404(Carpeta, id=carpeta_id)

    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.usuario = request.user
            archivo.carpeta = carpeta
            archivo.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ArchivoForm()
        return render(request, 'subir_archivo.html', {'form': form, 'carpeta': carpeta})
    

@login_required
def dashboard_usuario(request):
    carpetas = Carpeta.objects.filter(usuario=request.user)
    archivos = Archivo.objects.filter(usuario=request.user)
    return render(request, 'user_dashboard.html', {'carpetas': carpetas, 'archivos': archivos})



@login_required
def editar_archivo(request, archivo_id):
    archivo = get_object_or_404(Archivo, id=archivo_id, usuario=request.user)
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES, instance=archivo)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ArchivoForm(instance=archivo)
    return render(request, 'editar_archivo_form.html', {'form': form})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Archivo

@login_required
def eliminar_archivo(request, archivo_id):
    if request.method == 'POST':
        try:
            archivo = Archivo.objects.get(pk=archivo_id)
            
            # Permitir eliminar si es el dueño o si es admin
            if archivo.usuario == request.user or request.user.is_staff:
                archivo.archivo.delete()  # elimina el archivo físico
                archivo.delete()          # elimina el objeto en DB
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'No autorizado'})
        except Archivo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Archivo no encontrado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})



