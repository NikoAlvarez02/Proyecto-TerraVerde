from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .api_views import ProfesionalViewSet, ProfesionalHorarioViewSet

app_name = "profesionales"

router = DefaultRouter()
router.register(r"profesionales", ProfesionalViewSet, basename="profesionales")
router.register(r"profesionales-horarios", ProfesionalHorarioViewSet, basename="profesionales-horarios")

urlpatterns = [
    path("api/", include(router.urls)),
    # SPA por API
    path("", TemplateView.as_view(template_name="profesionales/profesionales_list.html"), name="list"),
]

#get
#post
#put
#delete
