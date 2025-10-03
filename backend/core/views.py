# # backend/core/views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def vista_admin_mod(request):
#     # Solo admins pueden entrar a esta pantalla
#     if not hasattr(request.user, "perfil") or request.user.perfil.rol != "admin":
#         # plantilla simple de “no autorizado”
#         return render(request, "administracion/no_autorizado.html", status=403)
#     return render(request, "administracion/administrador.html")
