from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .api_views import ProfesionalViewSet, ProfesionalHorarioViewSet, EspecialidadViewSet

app_name = "profesionales"

router = DefaultRouter()
router.register(r"profesionales", ProfesionalViewSet, basename="profesionales")
router.register(r"profesionales-horarios", ProfesionalHorarioViewSet, basename="profesionales-horarios")
router.register(r"especialidades", EspecialidadViewSet, basename="especialidades")

urlpatterns = [
    path("api/", include(router.urls)),
    # SPA por API
    path("", login_required(TemplateView.as_view(template_name="profesionales/profesionales_list.html")), name="list"),
]

#get
#post
#put
#delete
