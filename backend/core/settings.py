"""
Configuración de Django para el proyecto core.

Generado por 'django-admin startproject' usando Django 5.2.6.

Para más información sobre este archivo, ver
https://docs.djangoproject.com/en/5.2/topics/settings/

Para la lista completa de configuraciones y sus valores, ver
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import environ

# Construye rutas dentro del proyecto como BASE_DIR / 'subcarpeta'
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa las variables de entorno (lee el archivo .env)
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(BASE_DIR / '.env')

# Configuración rápida para desarrollo - no usar en producción
# Ver https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# ¡ATENCIÓN! Mantené la clave secreta fuera del código en producción
SECRET_KEY = env('SECRET_KEY')

# ¡ATENCIÓN! No uses debug en producción
DEBUG = env('DEBUG', default=True)

# Lista de hosts permitidos para acceder a la aplicación
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Personalización del Admin
ADMIN_SITE_HEADER = "TerraVerde Admin"
ADMIN_SITE_TITLE = "TerraVerde"
ADMIN_INDEX_TITLE = "Panel de Administración"

# Definición de aplicaciones instaladas
INSTALLED_APPS = [
    # Aplicaciones principales de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones de terceros
    'rest_framework',      # Django REST Framework para APIs
    'corsheaders',         # Manejo de CORS

    # Aplicaciones propias del proyecto
    'apps.pacientes',
    'apps.profesionales',
    'apps.turnos',
]

# Definición de middleware (procesadores de peticiones/respuestas)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Debe ir arriba de CommonMiddleware para CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Archivo principal de URLs
ROOT_URLCONF = 'core.urls'

# Configuración del admin
ADMIN_SITE_HEADER = "🌱 TerraVerde Admin"
ADMIN_SITE_TITLE = "TerraVerde"

# Configurar templates para admin personalizado
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR /"core" 'templates'],  # Asegúrate de que esta línea esté
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuración para WSGI (servidor web)
WSGI_APPLICATION = 'core.wsgi.application'

# Configuración de la base de datos
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DB_ENGINE = env('DB_ENGINE')

if DB_ENGINE == 'django.db.backends.postgresql':
    # Configuración para PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': env('DB_NAME'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }
else:
    # Configuración para SQLite (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Validadores de contraseñas
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internacionalización
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'es-ar'  # Idioma por defecto (español de Argentina)
TIME_ZONE = 'America/Argentina/Buenos_Aires'  # Zona horaria
USE_I18N = True           # Habilita la internacionalización
USE_TZ = True             # Usa zonas horarias

# Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'    # URL base para archivos estáticos

# Tipo de campo primario por defecto para modelos
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de CORS (permite consumir la API desde el frontend)
CORS_ALLOW_ALL_ORIGINS = True
# Para producción, es recomendable especificar orígenes específicos:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://localhost:5173",
# ]

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}