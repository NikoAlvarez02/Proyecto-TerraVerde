from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from rest_framework import viewsets, permissions
from .serializers import UsuarioSerializer
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .forms import SecurePasswordResetRequestForm

User = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]


@login_required
def usuarios_admin_view(request):
    u = request.user
    perfil = getattr(u, 'perfil', None)
    is_admin = (u.is_staff or (perfil and (getattr(perfil, 'rol', None) == 'admin' or getattr(perfil, 'puede_admin_usuarios', False))))
    if not is_admin:
        raise PermissionDenied("No autorizado")
    return render(request, 'usuarios/usuarios_list.html')


class SecurePasswordResetView(PasswordResetView):
    """Solicita usuario + email de recuperación y envía enlace si coinciden.

    No revela si la combinación es correcta; siempre muestra éxito.
    """

    form_class = SecurePasswordResetRequestForm

    def form_valid(self, form):
        user = form.get_matched_user()
        if user and user.email:
            # Reutilizar el flujo estándar para generar y enviar el email
            std_form = PasswordResetForm(data={"email": user.email})
            if std_form.is_valid():
                std_form.save(
                    request=self.request,
                    use_https=self.request.is_secure(),
                    email_template_name=self.email_template_name,
                    subject_template_name=self.subject_template_name,
                    html_email_template_name=self.html_email_template_name,
                    from_email=self.from_email,
                    extra_email_context=self.extra_email_context,
                    token_generator=self.token_generator,
                )
        # Siempre redirige a success_url, sin revelar estado
        return super().form_valid(form)
