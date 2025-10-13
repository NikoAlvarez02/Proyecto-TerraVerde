from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import CenterViewSet

app_name = 'centros'

router = DefaultRouter()
router.register(r'centros', CenterViewSet, basename='centros')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='centros/centros_list.html'), name='list'),
]
