from django.urls import reverse  # Додайте цей імпорт
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from .models import Account, Zone, Lamp, Dashboard, OutageSchedule


class BusinessLogicTests(APITestCase):
    def setUp(self):
        # Початкові дані
        self.account = Account.objects.create(username="admin", password_hash="123", role="admin")
        self.dashboard = Dashboard.objects.create(name="Test City", account=self.account)
        self.zone = Zone.objects.create(name="Highway 1", type="highway", dashboard=self.dashboard)
        # Створюємо лампу. Зверніть увагу: id створиться автоматично
        self.lamp = Lamp.objects.create(serial_number="L-001", zone=self.zone, latitude=0, longitude=0)
        # Отримуємо URL через name
        self.url = reverse('iot-telemetry')

    def test_adaptive_lighting_high_motion(self):
        """Перевірка: високий рівень руху вмикає світло на 100%"""
        data = {"lamp_id": self.lamp.id, "motion_level": 90, "consumption": 0.5}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 100)

    def test_outage_priority(self):
        """Перевірка: графік відключень має пріоритет над рухом"""
        now = timezone.now()
        OutageSchedule.objects.create(
            zone=self.zone,
            start_time=now - timezone.timedelta(hours=1),
            end_time=now + timezone.timedelta(hours=1)
        )

        data = {"lamp_id": self.lamp.id, "motion_level": 100, "consumption": 0.5}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['command'], "POWER_OFF")

    def test_faulty_detection(self):
        """Перевірка: якщо лампа має світити, але споживання 0 — статус 'faulty'"""
        data = {"lamp_id": self.lamp.id, "motion_level": 90, "consumption": 0}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Обов'язково оновлюємо об'єкт з бази даних перед перевіркою
        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.status, 'faulty')