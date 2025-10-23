# # apps/turnos/forms.py (CORREGIDO)
# from django import forms
# from .models import Turno

# class TurnoForm(forms.ModelForm):
#     class Meta:
#         model = Turno
#         # 1. Usamos 'fecha_hora' (el nombre real del modelo)
#         # 2. Usamos 'motivo' y 'observaciones' (los nombres reales del modelo)
#         fields = ["paciente", "profesional", "fecha_hora", "motivo", "observaciones"]
        
#         widgets = {
#             # 3. Usamos DateTimeInput para manejar el campo fecha_hora
#             #    Le aplicamos widgets de fecha y hora para una mejor experiencia de usuario.
#             "fecha_hora": forms.DateTimeInput(
#                 attrs={"type": "datetime-local"}, 
#                 format="%Y-%m-%dT%H:%M" # Formato requerido por el navegador
#             ),
#             # 4. Usamos Textarea para 'motivo' u 'observaciones'
#             "motivo": forms.Textarea(attrs={"rows": 2}), 
#             "observaciones": forms.Textarea(attrs={"rows": 4}),
#         }