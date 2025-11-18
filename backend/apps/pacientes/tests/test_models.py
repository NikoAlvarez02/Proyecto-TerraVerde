from datetime import date
from django.test import TestCase
from apps.pacientes.models import Paciente


class PacienteModelTest(TestCase):
    def test_crear_paciente(self):
        p = Paciente.objects.create(
            nombre="Ana",
            apellido="Pérez",
            dni="30123456",
            fecha_nacimiento=date(1990, 1, 1),
        )
        self.assertIsNotNone(p.id)
        self.assertIn("Ana", str(p))

