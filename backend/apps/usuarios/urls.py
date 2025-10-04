from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .api_views import UsuarioViewSet

app_name = "usuarios"

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", TemplateView.as_view(template_name="usuarios/usuarios_list.html"), name="list"),
]



    # from rest_framework.documentation import include_docs_urls
    # path("docs/", include_docs_urls(title="Usuarios API")),
#get
#post   
