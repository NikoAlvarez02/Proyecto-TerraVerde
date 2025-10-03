from pathlib import Path
import environ
import os

# ----------------------------
# Rutas base del proyecto
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../PROYECTO-TERRAVERDE/backend
ROOT_DIR = BASE_DIR.parent                         # .../PROYECTO-TERRAVERDE

# Estructura frontend (carpeta hermana)
FRONTEND_DIR = ROOT_DIR / "frontend"



# # --- Frontend ---
# FRONTEND_DIR = BASE_DIR / "frontend"
# FRONTEND_TEMPLATES_DIR = FRONTEND_DIR / "HTML"   # <— carpeta con MAYÚSCULAS

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

ADMIN_SITE_HEADER = "🌱 TerraVerde Admin"
ADMIN_SITE_TITLE = "TerraVerde"
ADMIN_INDEX_TITLE = "Panel de Administración"

INSTALLED_APPS = [
    # "core.apps.TerraVerdeAdminConfig",  # 👈 en lugar de 'django.contrib.admin'
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework','corsheaders','coreapi',
     'apps.pacientes','apps.profesionales','apps.turnos','apps.usuarios',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        FRONTEND_DIR / "EMAILS",  # <- para los txt de email
        FRONTEND_DIR / "HTML",           # p.ej. .../frontend/HTML/paginaprincipal.html
        FRONTEND_DIR / 'HTML' / 'pacientes',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    FRONTEND_DIR,                        # .../frontend/{CSS,JS,assets}
]

WSGI_APPLICATION = 'core.wsgi.application'

DB_ENGINE = env('DB_ENGINE', default='django.db.backends.sqlite3')
if DB_ENGINE == 'django.db.backends.postgresql':
    DATABASES = {'default': {
        'ENGINE': DB_ENGINE,
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }}
else:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [FRONTEND_DIR]  # frontend/CSS, frontend/JS, etc.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
# --- Email / Password Reset ---
# Desarrollo: muestra el email en la consola del runserver
# EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
# DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="martchaz84@gmail.com")

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="martinchazarretalapaz@gmail.com")

# Token de reset válido (por defecto 3 días). Opcional:
from datetime import timedelta
PASSWORD_RESET_TIMEOUT = int(timedelta(days=1).total_seconds())  # 1 día

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    }
