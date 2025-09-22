from django.urls import path
from .views import (
    PacienteListView, PacienteDetailView, PacienteCreateView,
    PacienteUpdateView, PacienteDeleteView
)

app_name = "pacientes"

urlpatterns = [
    path("", PacienteListView.as_view(), name="list"),
    path("nuevo/", PacienteCreateView.as_view(), name="create"),
    path("<int:pk>/", PacienteDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", PacienteUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", PacienteDeleteView.as_view(), name="delete"),
]
