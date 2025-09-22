from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            "dni", "nombre", "apellido", "fecha_nacimiento", "telefono",
            "email", "direccion", "obra_social", "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
        }
