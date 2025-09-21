from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Profesional
from .forms import ProfesionalForm

class ProfesionalListView(ListView):
    model = Profesional
    paginate_by = 10
    template_name = "profesionales/list.html"

class ProfesionalDetailView(DetailView):
    model = Profesional
    template_name = "profesionales/detail.html"

class ProfesionalCreateView(CreateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = "profesionales/form.html"
    success_url = reverse_lazy("profesionales:list")

class ProfesionalUpdateView(UpdateView):
    model = Profesional
    form_class = ProfesionalForm
    template_name = "profesionales/form.html"
    success_url = reverse_lazy("profesionales:list")

class ProfesionalDeleteView(DeleteView):
    model = Profesional
    template_name = "profesionales/confirm_delete.html"
    success_url = reverse_lazy("profesionales:list")
