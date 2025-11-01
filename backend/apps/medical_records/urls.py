from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter
from .views import ObservationViewSet

app_name = 'historias'

router = DefaultRouter()
router.register(r'observaciones', ObservationViewSet, basename='observaciones')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', login_required(TemplateView.as_view(template_name='historia_clinica.html')), name='historia'),
]
