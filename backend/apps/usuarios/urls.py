from django.urls import path, include
from rest_framework import routers
# from rest_framework.documentation import include_docs_urls
from .views import UsuarioViewSet   # <-- nombre correcto

router = routers.DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
app_name = "usuarios"  # para usar {% url 'usuarios:list' %}
urlpatterns = [
    path("api/", include(router.urls)),
    # podés quitar docs aquí; ver punto 3
    # path("docs/", include_docs_urls(title="Usuarios API")),
]
