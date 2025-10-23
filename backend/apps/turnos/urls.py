from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .api_views import TurnoViewSet  # o desde .views si lo dejaste ahí

app_name = "turnos"

router = DefaultRouter()
router.register(r"turnos", TurnoViewSet, basename="turnos")

urlpatterns = [
    path("api/", include(router.urls)),
    # SPA (lista + modal CRUD por API)
    path("", TemplateView.as_view(template_name="turnos/turnos_list.html"), name="list"),
]

#get
#post
#put
#delete
