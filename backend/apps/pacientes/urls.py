# apps/pacientes/urls.py
from django.urls import path, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import PacienteViewSet

app_name = "pacientes"  # para usar {% url 'pacientes:list' %}

router = routers.DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='pacientes')

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "listado/",
        login_required(TemplateView.as_view(template_name="pacientes_list.html")),
        name="list",
    ),
]

 
#get
#post
#put
#delete