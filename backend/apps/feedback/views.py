from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.urls import reverse

from apps.pacientes.models import Paciente
from apps.profesionales.models import Profesional
from .models import Satisfaccion


@login_required
def lista_satisfaccion(request):
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        profesional_id = request.POST.get('profesional')
        puntaje = request.POST.get('puntaje')
        comentario = request.POST.get('comentario', '').strip()
        try:
            paciente = Paciente.objects.get(pk=paciente_id)
            profesional = Profesional.objects.filter(pk=profesional_id).first() if profesional_id else None
            puntaje_i = int(puntaje)
            if puntaje_i < 1 or puntaje_i > 5:
                raise ValueError("puntaje fuera de rango")
            Satisfaccion.objects.create(
                paciente=paciente,
                profesional=profesional,
                puntaje=puntaje_i,
                comentario=comentario,
            )
            return redirect(reverse('satisfaccion:list'))
        except Exception:
            pass  # Silencioso: en una mejora podemos mostrar mensajes

    calificaciones = Satisfaccion.objects.select_related('paciente', 'profesional')[:50]
    pacientes = Paciente.objects.filter(activo=True).order_by('apellido', 'nombre')[:200]
    profesionales = Profesional.objects.filter(activo=True).order_by('apellido', 'nombre')[:200]
    promedio = calificaciones.aggregate(avg=Avg('puntaje')).get('avg')

    return render(request, 'satisfaccion/list.html', {
        'calificaciones': calificaciones,
        'pacientes': pacientes,
        'profesionales': profesionales,
        'promedio': promedio,
    })

