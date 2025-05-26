from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime

class CalendarioApiTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_calendario_api_dias_mes_actual(self):
        """Comprueba que la API de calendario devuelve eventos para el mes actual."""
        today = datetime.now()
        url = reverse('calendario_api')
        response = self.client.get(url, {
            'year': today.year,
            'month': today.month,
            'blue': 'False',
            'duracion': 30
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers['Content-Type'].startswith('application/json'))
        eventos = response.json()
        self.assertIsInstance(eventos, list)
        # Opcional: comprobar que hay al menos un evento en el mes
        self.assertGreater(len(eventos), 0)
