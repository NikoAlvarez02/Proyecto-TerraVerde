from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import ObservationViewSet

app_name = 'historias'

router = DefaultRouter()
router.register(r'observaciones', ObservationViewSet, basename='observaciones')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='historia_clinica.html'), name='historia'),
]
