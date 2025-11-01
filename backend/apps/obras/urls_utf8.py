from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import ObraSocialViewSet, PlanObraSocialViewSet, ObraSocialImportView


app_name = 'obras'

router = DefaultRouter()
router.register(r'obras-sociales', ObraSocialViewSet, basename='obras_sociales')
router.register(r'planes', PlanObraSocialViewSet, basename='planes_obras')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/import/snrs/', ObraSocialImportView.as_view(), name='obras_import_snrs'),
    # SPA para gestionar obras sociales vÃ­a API
    path('', TemplateView.as_view(template_name='obras/obras_list.html'), name='list'),
]

