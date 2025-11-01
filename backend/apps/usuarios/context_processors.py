def perfil_permisos(request):
    u = getattr(request, 'user', None)
    perfil = getattr(u, 'perfil', None) if u and u.is_authenticated else None
    return {
        'perfil': perfil,
    }

