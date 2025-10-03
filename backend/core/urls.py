# backend/core/urls.py
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls

# Personalizar títulos del admin
admin.site.site_header = "🌱 Administración TerraVerde"
admin.site.site_title = "TerraVerde Admin"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "admin-mod/",
        login_required(TemplateView.as_view(template_name="administrador.html")),
        name="admin_mod",
    ),

    # Apps con namespace
    path("turnos/", include(("apps.turnos.urls", "turnos"), namespace="turnos")),
    path("pacientes/", include(("apps.pacientes.urls", "pacientes"), namespace="pacientes")),
    path("profesionales/", include(("apps.profesionales.urls", "profesionales"), namespace="profesionales")),
    path("usuarios/", include(("apps.usuarios.urls", "usuarios"), namespace="usuarios")),

    path("api/docs/", include_docs_urls(title="TerraVerde API")),
    path("", login_required(TemplateView.as_view(template_name="paginaprincipal.html")), name="home"),
    # ... resto (login, logout, reset, etc.)

    
   
    # Home (requiere login)

    # Auth
    path("login/",  LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Password reset
    path(
        "password-reset/",
        PasswordResetView.as_view(
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
