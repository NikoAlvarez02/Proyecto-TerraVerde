# core/apps.py
from django.contrib.admin.apps import AdminConfig

class TerraVerdeAdminConfig(AdminConfig):
    default_site = "core.admin.TerraVerdeAdminSite"
    verbose_name = "Administración TerraVerde"