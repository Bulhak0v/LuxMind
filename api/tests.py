from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from .models import Account, Zone, Lamp, Dashboard, OutageSchedule


class BusinessLogicTests(APITestCase):
    def setUp(self):
        self.account = Account.objects.create(username="admin", password_hash="123", role="admin")
        self.dashboard = Dashboard.objects.create(name="Test City", account=self.account)
        self.zone = Zone.objects.create(name="Highway 1", type="highway", dashboard=self.dashboard)

        self.lamp = Lamp.objects.create(
            serial_number="L-001",
            zone=self.zone,
            latitude=50.45,
            longitude=30.52
        )

        self.url = reverse('iot-telemetry')

    def test_adaptive_lighting_high_motion(self):
        data = {"id": self.lamp.id, "motion_level": 90, "consumption": 0.5}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 100)

    def test_outage_priority(self):
        now = timezone.now()
        OutageSchedule.objects.create(
            zone=self.zone,
            start_time=now - timezone.timedelta(hours=1),
            end_time=now + timezone.timedelta(hours=1)
        )

        data = {"id": self.lamp.id, "motion_level": 100, "consumption": 0.5}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['command'], "POWER_OFF")
        self.assertEqual(response.data['reason'], "Outage active")

    def test_faulty_detection(self):
        data = {"id": self.lamp.id, "motion_level": 90, "consumption": 0}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lamp.refresh_from_db()
        self.assertEqual(self.lamp.status, 'faulty')
        self.assertEqual(self.lamp.current_brightness, 0)
