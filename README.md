# 📁 Sistema de Gestión de Archivos Académicos

Un sistema web desarrollado en Django para la gestión y organización de archivos académicos por períodos, diseñado para instituciones educativas que necesitan administrar documentos de manera estructurada y eficiente.

## 🚀 Características Principales

- **Gestión de Períodos Académicos**: Organización por períodos académicos con fechas de inicio y fin
- **Sistema de Carpetas Jerárquico**: Carpetas principales y subcarpetas para mejor organización
- **Control de Acceso**: Diferenciación entre administradores y usuarios regulares
- **Archivos Públicos/Privados**: Control de visibilidad de carpetas y archivos
- **Descarga de Carpetas**: Exportación completa de carpetas en formato ZIP
- **Interfaz Intuitiva**: Dashboard moderno y responsivo
- **Gestión de Usuarios**: Los administradores pueden crear y gestionar usuarios

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.7
- **Base de Datos**: SQLite (por defecto)
- **Frontend**: HTML5, CSS3, JavaScript
- **Archivos**: Sistema de archivos local con soporte para múltiples formatos

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

## 🔧 Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/drive-academico.git
cd drive-academico
```

### 2. Crear Entorno Virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Administrador del Sistema

```bash
python manage.py create_admin
```

Este comando creará un superusuario con las siguientes credenciales:
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **Email**: `admin@drive.com`

> ⚠️ **IMPORTANTE**: Cambia la contraseña después del primer login por seguridad.

### 6. Crear Carpetas de Medios

Las carpetas necesarias ya están incluidas en el repositorio:
- `media/` - Para archivos subidos por usuarios
- `media/archivos/` - Subcarpeta donde Django guarda los archivos
- `static/` - Para archivos estáticos adicionales

> **Nota**: Los archivos físicos se almacenan en `media/archivos/` mientras que las referencias se guardan en la base de datos.

### 7. Ejecutar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://127.0.0.1:8000/`

## 👤 Primer Acceso

1. Accede a `http://127.0.0.1:8000/`
2. Inicia sesión con:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`
3. **Cambia inmediatamente la contraseña** desde el panel de administración
4. Crea tu primer período académico
5. Comienza a organizar tus archivos

## 📁 Estructura del Proyecto

```
drive-academico/
├── AppPrincipal/           # Aplicación principal
│   ├── migrations/         # Migraciones de base de datos
│   ├── static/            # Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/         # Plantillas HTML
│   ├── management/        # Comandos personalizados
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Lógica de vistas
│   ├── forms.py           # Formularios
│   └── urls.py            # URLs de la aplicación
├── miapp/                 # Configuración del proyecto
│   ├── settings.py        # Configuraciones
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuración WSGI
├── media/                 # Archivos subidos por usuarios
│   ├── archivos/          # Archivos físicos organizados por Django
│   └── .gitkeep           # Mantiene la estructura en Git
├── static/                # Archivos estáticos recolectados
├── requirements.txt       # Dependencias del proyecto
├── manage.py              # Utilidad de gestión de Django
└── README.md              # Este archivo
```

## 🔐 Roles de Usuario

### Administrador
- Crear y gestionar períodos académicos
- Crear y gestionar usuarios
- Crear carpetas y subcarpetas
- Subir y gestionar archivos
- Controlar visibilidad de carpetas
- Exportar períodos completos

### Usuario Regular
- Ver carpetas públicas
- Subir archivos a carpetas permitidas
- Descargar archivos disponibles
- Gestionar sus propios archivos

## 📊 Funcionalidades Principales

### Gestión de Períodos
- Crear períodos académicos con fechas específicas
- Activar/desactivar períodos
- Organizar contenido por período

### Sistema de Carpetas
- Carpetas principales por categorías predefinidas
- Subcarpetas para mejor organización
- Control de visibilidad (público/privado)

### Gestión de Archivos
- Subida de múltiples formatos
- Organización automática por carpetas
- Descarga individual o masiva
- Control de acceso por usuario

## 🚀 Comandos Útiles

### Crear Superusuario Adicional
```bash
python manage.py createsuperuser
```

### Recolectar Archivos Estáticos (Producción)
```bash
python manage.py collectstatic
```

### Limpiar Base de Datos
```bash
python manage.py flush
```

### Ejecutar Tests
```bash
python manage.py test
```

## 🔧 Configuración Adicional

### Variables de Entorno (Producción)
Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
```

### Base de Datos PostgreSQL (Opcional)
Para usar PostgreSQL en lugar de SQLite:

1. Instalar psycopg2:
```bash
pip install psycopg2-binary
```

2. Modificar `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nombre_de_tu_base_de_datos',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
```bash
pip install django==4.2.7
```

### Error: "Permission denied" en archivos
```bash
# En Linux/macOS
chmod +x manage.py
```

### Error de migraciones
```bash
python manage.py makemigrations --empty AppPrincipal
python manage.py migrate
```

### Resetear contraseña de administrador
```bash
python manage.py changepassword admin
```


**Desarrollado con ❤️ para la gestión académica eficiente**