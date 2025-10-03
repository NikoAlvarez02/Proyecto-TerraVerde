from django.urls import path, include
from rest_framework import routers
# Si usás docs globales en core/urls.py, podés omitir include_docs_urls acá
from .views import ProfesionalViewSet   # <- nombre correcto

router = routers.DefaultRouter()
router.register(r'profesionales', ProfesionalViewSet, basename='profesionales')

app_name = "profesionales"  # para usar {% url 'profesionales:list' %}  
urlpatterns = [
    path("api/", include(router.urls)),   # convención en minúsculas
    # path("docs/", include_docs_urls(title="Profesionales API")),  # opcional
]

#get
#post
#put
#delete