from django.urls import path
from . import views

app_name = 'geo'

urlpatterns = [
    path('provincias/', views.ProvinciasView.as_view(), name='provincias'),
    path('municipios/', views.MunicipiosView.as_view(), name='municipios'),
    path('localidades/', views.LocalidadesView.as_view(), name='localidades'),
    path('departamentos/', views.DepartamentosView.as_view(), name='departamentos'),
]

