from datetime import date
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.pacientes.models import Paciente


class PacientesApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="12345678")
        self.client = APIClient()
        self.client.login(username="tester", password="12345678")  # Session auth

    def test_listado_pacientes(self):
        Paciente.objects.create(nombre="Ana", apellido="Pérez", dni="30123456", fecha_nacimiento=date(1990, 1, 1))
        resp = self.client.get("/pacientes/api/pacientes/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # En este proyecto la vista devuelve lista plana (sin paginar)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

