from django.urls import path, include
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import TurnoViewSet

app_name = "turnos"  # <- para usar {% url 'turnos:list' %}

router = routers.DefaultRouter()
router.register(r'turnos', TurnoViewSet, basename='turnos')

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "listado/",
        login_required(TemplateView.as_view(template_name="turnos_list.html")),
        name="list",  # <- nombre que usará el template
    ),
]

#get
#post
#put
#delete
