from rest_framework import serializers
from .models import (
    Account, Dashboard, Zone, Lamp, Sensor,
    SensorData, OutageSchedule, EnergyConsumption, Backup
)

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'password_hash', 'role', 'email', 'created_at', ]
        read_only_fields = ['created_at']
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ['id', 'name', 'description', 'created_at', 'account']
        read_only_fields = ['created_at', 'account']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'type', 'priority', 'description', 'dashboard']
        read_only_fields = ['dashboard']

class LampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lamp
        fields = ['id', 'serial_number', 'latitude', 'longitude',
                  'current_brightness', 'status', 'installed_at', 'zone']
        read_only_fields = ['installed_at']

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['id', 'type', 'lamp']

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['id', 'timestamp', 'value', 'sensor']
        read_only_fields = ['timestamp']

class OutageScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutageSchedule
        fields = ['id', 'start_time', 'end_time', 'description', 'zone']

class EnergyConsumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyConsumption
        fields = ['id', 'timestamp', 'amount_kwh', 'lamp']
        read_only_fields = ['timestamp']

class BackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = ['id', 'created_at', 'file_path', 'type', 'description', 'account']
        read_only_fields = ['created_at']

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    id = serializers.IntegerField()
    role = serializers.CharField()

class IoTTelemetrySerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID світильника (Lamp ID)")
    motion_level = serializers.IntegerField(min_value=0, max_value=100, help_text="Рівень руху 0-100")
    consumption = serializers.FloatField(min_value=0, help_text="Поточне споживання у Вт")
    ambient_light = serializers.IntegerField(min_value=0, max_value=4095,
                                             help_text="Рівень світла від фоторезистора (0-4095)")

class EnergyAnalyticsSerializer(serializers.Serializer):
    actual_kwh = serializers.FloatField()
    savings_percent = serializers.FloatField()

class SystemHealthSerializer(serializers.Serializer):
    total_lamps = serializers.IntegerField()
    faulty_lamps = serializers.IntegerField()
    active_outages = serializers.IntegerField()
    total_users = serializers.IntegerField()

class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()