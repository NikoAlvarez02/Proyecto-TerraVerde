from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .api_views import UsuarioViewSet
from .views import usuarios_admin_view

app_name = "usuarios"

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", usuarios_admin_view, name="list"),
]



    # from rest_framework.documentation import include_docs_urls
    # path("docs/", include_docs_urls(title="Usuarios API")),
#get
#post   
