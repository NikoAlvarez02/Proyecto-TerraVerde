from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

class TerraVerdeAdminSite(AdminSite):
    # Títulos del admin
    site_header = "TerraVerde Admin"
    site_title = "TerraVerde"
    index_title = "Panel de Administración TerraVerde"
    
    # Texto del login
    login_template = 'admin/login.html'
    
    def each_context(self, request):
        """Agregar contexto personalizado"""
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'site_url': '/',
        })
        return context

# Reemplazar el admin por defecto
admin.site = TerraVerdeAdminSite()
admin.sites.site = admin.site