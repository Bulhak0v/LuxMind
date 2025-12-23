import json
from django.core import serializers
from django.utils import timezone
from django.db.models import Sum, F
from .models import Lamp, OutageSchedule, EnergyConsumption, SensorData, Zone, Account, Backup
from decimal import Decimal


class LightingService:
    @staticmethod
    def check_outage_active(zone_id):
        now = timezone.now()
        return OutageSchedule.objects.filter(
            zone_id=zone_id,
            start_time__lte=now,
            end_time__gte=now
        ).exists()

    @staticmethod
    def calculate_adaptive_brightness(lamp, sensor_value):
        zone_type = lamp.zone.type
        MIN_BRIGHTNESS = {'highway': 40, 'residential': 20, 'park': 10}
        base_min = MIN_BRIGHTNESS.get(zone_type, 10)
        return 100 if sensor_value > 50 else base_min

    @staticmethod
    def process_iot_telemetry(id, motion_level, current_consumption): # Змінено lamp_id -> id
        lamp = Lamp.objects.get(pk=id)

        if LightingService.check_outage_active(lamp.zone_id):
            lamp.status = 'inactive'
            lamp.current_brightness = 0
            lamp.save()
            return {"command": "POWER_OFF", "reason": "Outage active"}

        new_brightness = LightingService.calculate_adaptive_brightness(lamp, motion_level)

        if new_brightness > 0 and current_consumption <= 0:
            lamp.status = 'faulty'
            new_brightness = 0
        else:
            lamp.status = 'active'

        lamp.current_brightness = new_brightness
        lamp.save()
        return {"command": "SET_BRIGHTNESS", "value": new_brightness}

    @staticmethod
    def get_energy_savings(id, days=30):
        start_date = timezone.now() - timezone.timedelta(days=days)
        actual_total = EnergyConsumption.objects.filter(
            lamp__zone__dashboard_id=id,
            timestamp__gte=start_date
        ).aggregate(total=Sum('amount_kwh'))['total'] or Decimal('0.0')  # Додайте Decimal тут

        theoretical_total = actual_total * Decimal('1.45')

        if theoretical_total > 0:
            savings_percent = ((theoretical_total - actual_total) / theoretical_total) * 100
        else:
            savings_percent = 0

        return {
            "actual_kwh": round(float(actual_total), 2),
            "savings_percent": round(float(savings_percent), 1)
        }


class AdminService:
    @staticmethod
    def get_system_health_report():
        return {
            "total_lamps": Lamp.objects.count(),
            "faulty_lamps": Lamp.objects.filter(status='faulty').count(),
            "active_outages": OutageSchedule.objects.filter(
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now()
            ).count(),
            "total_users": Account.objects.count()
        }

    @staticmethod
    def create_system_backup(id, backup_type='data'):  # Змінено account_id -> id
        data = Lamp.objects.all()
        file_name = f"backup_{backup_type}_{timezone.now().strftime('%Y%m%d')}.json"

        backup = Backup.objects.create(
            account_id=id,
            type=backup_type,
            file_path=f"/storage/backups/{file_name}",
            description=f"Системний бекап {backup_type}."
        )
        return backup