# backend/core/urls.py
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views as core_views
from apps.usuarios.views import SecurePasswordResetView

# Personalizar títulos del admin
admin.site.site_header = "Administración TerraVerde"
admin.site.site_title = "TerraVerde Admin"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "admin-mod/",
        login_required(TemplateView.as_view(template_name='administracion/administrador.html')),
        name="admin_mod",
    ),

    # Apps con namespace
    path("turnos/", include(("apps.turnos.urls", "turnos"), namespace="turnos")), 
    path("pacientes/", include(("apps.pacientes.urls", "pacientes"), namespace="pacientes")),
    path("profesionales/", include(("apps.profesionales.urls", "profesionales"), namespace="profesionales")),
    path("usuarios/", include(("apps.usuarios.urls", "usuarios"), namespace="usuarios")),
    path("centros/", include(("apps.centers.urls", "centros"), namespace="centros")),
    path("historias/", include(("apps.medical_records.urls", "historias"), namespace="historias")),
    path("obras/", include(("apps.obras.urls", "obras"), namespace="obras")),
    path("geo/", include(("apps.geo.urls", "geo"), namespace="geo")),
    path("reportes/", include(("apps.reports.urls", "reportes"), namespace="reportes")),
    path("satisfaccion/", include(("apps.feedback.urls", "satisfaccion"), namespace="satisfaccion")),
   
    # OpenAPI schema + UIs (drf-spectacular)
    # Servir docs usando schema.json fijo para evitar OSError en Windows
    path("api/schema/", core_views.serve_schema_json, name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", core_views.home_dashboard, name="home"),
    path("weasy/pdf/", core_views.weasy_pdf_test, name="weasy_pdf_test"),
    path("weasy/diagnostico/", core_views.weasy_diagnostico, name="weasy_diagnostico"),

    # Auth
    path("login/",  core_views.SessionLoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Password reset
    path(
        "password-reset/",
        SecurePasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="password_reset_email.txt",
            html_email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]

# Servir media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
