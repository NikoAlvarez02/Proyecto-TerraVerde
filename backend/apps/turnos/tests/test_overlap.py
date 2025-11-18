from datetime import date, time
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.pacientes.models import Paciente
from apps.profesionales.models import Profesional


class TurnoOverlapTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="12345678")
        self.client = APIClient()
        self.client.login(username="tester", password="12345678")

        self.paciente = Paciente.objects.create(
            nombre="Ana",
            apellido="Pérez",
            dni="30123456",
            fecha_nacimiento=date(1990, 1, 1),
        )
        self.profesional = Profesional.objects.create(
            nombre="Laura",
            apellido="Gómez",
            dni="20999888",
            matricula="ABC123",
            email="laura@example.com",
        )

    def test_overlap_same_hour_block(self):
        # Crear primer turno 10:00
        payload = {
            "fecha": "2025-01-01",
            "hora": "10:00",
            "paciente": self.paciente.id,
            "profesional": self.profesional.id,
            "estado": "pendiente",
        }
        r1 = self.client.post("/turnos/api/turnos/", payload, format='json')
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

        # Intentar otro turno a las 10:30 (debe rechazar por solapamiento)
        payload2 = dict(payload)
        payload2["hora"] = "10:30"
        r2 = self.client.post("/turnos/api/turnos/", payload2, format='json')
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hora', r2.data)
        self.assertIn('Profesional con turno en el horario', str(r2.data['hora']))

    def test_exact_same_time_conflict(self):
        payload = {
            "fecha": "2025-01-01",
            "hora": "09:00",
            "paciente": self.paciente.id,
            "profesional": self.profesional.id,
            "estado": "pendiente",
        }
        r1 = self.client.post("/turnos/api/turnos/", payload, format='json')
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        # Mismo horario exacto
        r2 = self.client.post("/turnos/api/turnos/", payload, format='json')
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hora', r2.data)
