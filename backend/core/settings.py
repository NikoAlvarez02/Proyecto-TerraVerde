from pathlib import Path
import environ
import os
from datetime import timedelta

# ----------------------------
# Rutas base del proyecto
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../PROYECTO-TERRAVERDE/backend
ROOT_DIR = BASE_DIR.parent                         # .../PROYECTO-TERRAVERDE

# Estructura frontend (carpeta hermana)
FRONTEND_DIR = ROOT_DIR / "frontend"

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

ADMIN_SITE_HEADER = "🌱 TerraVerde Admin"
ADMIN_SITE_TITLE = "TerraVerde"
ADMIN_INDEX_TITLE = "Panel de Administración"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'apps.pacientes',
    'apps.profesionales',
    'apps.turnos',
    'apps.usuarios',
    'apps.centers',
    'apps.medical_records',
    'apps.reports',
    'apps.feedback',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Registrar auditoría después de que el usuario esté resuelto
    "apps.usuarios.middleware.AuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        FRONTEND_DIR / "EMAILS",
        FRONTEND_DIR / "HTML",
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'apps.usuarios.context_processors.perfil_permisos',
        ],
    },
}]

WSGI_APPLICATION = 'core.wsgi.application'

# ----------------------------
# Base de datos
# ----------------------------
DB_ENGINE = env('DB_ENGINE', default='django.db.backends.sqlite3')
if DB_ENGINE == 'django.db.backends.postgresql':
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
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ----------------------------
# Validación de contraseñas
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# Internacionalización
# ----------------------------
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# ----------------------------
# Archivos estáticos
# ----------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    ('ASSETS', FRONTEND_DIR / 'ASSETS'),
    ('CSS', FRONTEND_DIR / 'CSS'),
    ('JS', FRONTEND_DIR / 'JS'),
]

# **MODIFICACIÓN CLAVE:**
# STATIC_ROOT se define SÓLO si la variable de entorno STATIC_ROOT_DEPLOY está presente
STATIC_ROOT_DEPLOY = env('STATIC_ROOT_DEPLOY', default=None)

if STATIC_ROOT_DEPLOY:
    STATIC_ROOT = ROOT_DIR / STATIC_ROOT_DEPLOY
else:
    # Si no está definida (ej. en desarrollo), Django no intentará usarla.
    # Se añade un PASS o una ruta nula para evitar errores de ImproperlyConfigured en local,
    # aunque en producción se requiere. Para forzar un error en desarrollo si se llama, 
    # se podría dejar en None o usar un entorno condicional, pero esto es más seguro.
    pass

# ----------------------------
# Autenticación
# ----------------------------
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ----------------------------
# CORS
# ----------------------------
# Permitir todo en DEBUG; en producción, configurar CORS_ALLOWED_ORIGINS
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=DEBUG)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"

# ----------------------------
# Media (uploads)
# ----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ----------------------------
# Django REST Framework (UNIFICADO)
# ----------------------------
REST_FRAMEWORK = {
    # Schema (OpenAPI)
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # Formatos
    'DATETIME_FORMAT': 'iso-8601',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    'DATE_INPUT_FORMATS': ['%Y-%m-%d', '%d/%m/%Y', 'iso-8601'],
    'TIME_INPUT_FORMATS': ['%H:%M', '%H:%M:%S', '%H:%M:%S.%f', 'iso-8601'],
    'DATETIME_INPUT_FORMATS': [
        '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', 'iso-8601'
    ],

    # Permisos por defecto (SOLO para pruebas)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,

    # Si más adelante querés auth, descomentá y elegí uno:
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.TokenAuthentication',  # para usar tokens
    #     # 'rest_framework.authentication.SessionAuthentication',  # Navegador (requiere CSRF; Thunder falla)
    # ],
}

# ----------------------------
# drf-spectacular (OpenAPI)
# ----------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'TerraVerde API',
    'DESCRIPTION': 'Documentación de la API TerraVerde',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ----------------------------
# Email / Password Reset
# ----------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="martinchazarretalapaz@gmail.com")

# Token de reset válido por 1 día
PASSWORD_RESET_TIMEOUT = int(timedelta(days=1).total_seconds())

# ----------------------------
# Simple JWT
# ----------------------------
from datetime import timedelta as _td
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': _td(minutes=60),
    'REFRESH_TOKEN_LIFETIME': _td(days=7),
}


