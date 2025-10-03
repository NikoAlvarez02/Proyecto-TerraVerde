# core/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite

class TerraVerdeAdminSite(AdminSite):
    site_header = "Administración TerraVerde"   # encabezado grande
    site_title = "TerraVerde"                   # <title> del HTML
    index_title = "Panel de Administración TerraVerde"
    login_template = "administracion/login.html"         # si querés login custom (opcional)

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx.update({"site_header": self.site_header, "site_title": self.site_title, "site_url": "/"})
        return ctx

# # Reemplaza el sitio por defecto
# admin.site = TerraVerdeAdminSite(name="terrav")  # ← poner un name explícito ayuda
# admin.sites.site = admin.site
