from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Paciente
from .forms import PacienteForm

class PacienteListView(ListView):
    model = Paciente
    paginate_by = 10
    template_name = "pacientes/list.html"

class PacienteDetailView(DetailView):
    model = Paciente
    template_name = "pacientes/detail.html"

class PacienteCreateView(CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/form.html"
    success_url = reverse_lazy("pacientes:list")

class PacienteUpdateView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = "pacientes/form.html"
    success_url = reverse_lazy("pacientes:list")

class PacienteDeleteView(DeleteView):
    model = Paciente
    template_name = "pacientes/confirm_delete.html"
    success_url = reverse_lazy("pacientes:list")
