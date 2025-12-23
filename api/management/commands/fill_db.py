import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import (
    Account, Dashboard, Zone, Lamp, Sensor,
    SensorData, OutageSchedule, EnergyConsumption
)


class Command(BaseCommand):
    help = 'Заповнює базу даних тестовими даними для проекту LuxMind'

    def handle(self, *args, **kwargs):
        self.stdout.write('Початок заповнення БД...')

        # 1. Створення акаунтів
        admin_user, _ = Account.objects.get_or_create(
            username='admin_nure',
            defaults={'password_hash': 'admin123', 'role': 'admin', 'email': 'admin@nure.ua'}
        )
        operator_user, _ = Account.objects.get_or_create(
            username='operator_1',
            defaults={'password_hash': 'op123', 'role': 'operator', 'email': 'op1@nure.ua'}
        )

        # 2. Дашборд
        kyiv_dashboard, _ = Dashboard.objects.get_or_create(
            name='Київ: Розумне світло',
            defaults={'description': 'Центральний проект управління освітленням столиці', 'account': admin_user}
        )

        # 3. Зони
        zones_data = [
            {'name': 'Парк Шевченка', 'type': 'park', 'priority': 1},
            {'name': 'Проспект Перемоги', 'type': 'highway', 'priority': 10},
            {'name': 'ЖК "Комфорт Таун"', 'type': 'residential', 'priority': 5},
        ]

        created_zones = []
        for z in zones_data:
            zone, _ = Zone.objects.get_or_create(
                name=z['name'],
                defaults={'type': z['type'], 'priority': z['priority'], 'dashboard': kyiv_dashboard}
            )
            created_zones.append(zone)

        # 4. Світильники (Lamps)
        # Координати центру Києва приблизно: 50.4501, 30.5234
        for i in range(15):
            zone = random.choice(created_zones)
            lamp = Lamp.objects.create(
                serial_number=f'LM-{1000 + i}',
                latitude=50.45 + (random.uniform(-0.01, 0.01)),
                longitude=30.52 + (random.uniform(-0.01, 0.01)),
                current_brightness=random.randint(0, 100),
                status=random.choice(['active', 'active', 'faulty']),  # Більше активних
                zone=zone
            )

            # 5. Сенсори для кожної лампи
            Sensor.objects.create(lamp=lamp, type='motion')
            sensor_light = Sensor.objects.create(lamp=lamp, type='light')

            # 6. Дані сенсорів (SensorData) та Споживання (EnergyConsumption) за останні 24 години
            for hour in range(24):
                timestamp = timezone.now() - timezone.timedelta(hours=hour)

                # Дані про освітленість
                SensorData.objects.create(
                    sensor=sensor_light,
                    timestamp=timestamp,
                    value={'lux': random.randint(10, 500)}
                )

                # Логи споживання енергії
                EnergyConsumption.objects.create(
                    lamp=lamp,
                    timestamp=timestamp,
                    amount_kwh=random.uniform(0.1, 0.5)
                )

        # 7. Графік відключень (OutageSchedule) - створюємо одне на сьогодні
        OutageSchedule.objects.create(
            zone=created_zones[1],  # Проспект Перемоги
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            description='Планове відключення мережі ДТЕК'
        )

        self.stdout.write(self.style.SUCCESS('Базу даних успішно заповнено!'))