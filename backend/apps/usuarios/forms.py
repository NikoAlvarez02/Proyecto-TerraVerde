from django import forms
from django.contrib.auth import get_user_model
from .models import Perfil


class SecurePasswordResetRequestForm(forms.Form):
    username = forms.CharField(label="Usuario", max_length=150)
    recovery_email = forms.EmailField(label="Email de recuperación")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._matched_user = None

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        rec_email = cleaned.get("recovery_email")
        if not username or not rec_email:
            return cleaned

        User = get_user_model()
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            # No revelamos existencia; no marcamos error
            self._matched_user = None
            return cleaned

        perfil = getattr(user, "perfil", None)
        if perfil and getattr(perfil, "email_recuperacion", None):
            if str(perfil.email_recuperacion).strip().lower() == str(rec_email).strip().lower():
                self._matched_user = user
        # Si no coincide, no seteamos error para evitar enumeración
        return cleaned

    def get_matched_user(self):
        return self._matched_user

