from django.urls import path
from .views import (
    ProfesionalListView, ProfesionalDetailView, ProfesionalCreateView,
    ProfesionalUpdateView, ProfesionalDeleteView
)

app_name = "profesionales"

urlpatterns = [
    path("", ProfesionalListView.as_view(), name="list"),
    path("nuevo/", ProfesionalCreateView.as_view(), name="create"),
    path("<int:pk>/", ProfesionalDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", ProfesionalUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", ProfesionalDeleteView.as_view(), name="delete"),
]
