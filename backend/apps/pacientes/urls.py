from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .api_views import PacienteViewSet   # 👈 ahora sí existe

app_name = "pacientes"

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet, basename='pacientes')

urlpatterns = [
    path("api/", include(router.urls)),
    path("", TemplateView.as_view(template_name="pacientes/pacientes_list.html"), name="list"),
]

 
#get
#post
#put
#delete