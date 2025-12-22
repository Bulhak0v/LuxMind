from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Account(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('operator', 'Operator'),
    ]

    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Dashboard(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='dashboards')

    def __str__(self):
        return self.name


class Zone(models.Model):
    TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('highway', 'Highway'),
        ('park', 'Park'),
    ]

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    priority = models.IntegerField(default=5)
    description = models.TextField(null=True, blank=True)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='zones')

    def __str__(self):
        return self.name


class Lamp(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('faulty', 'Faulty'),
    ]

    serial_number = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    current_brightness = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    installed_at = models.DateTimeField(auto_now_add=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='lamps')

    def __str__(self):
        return self.serial_number


class Sensor(models.Model):
    TYPE_CHOICES = [
        ('motion', 'Motion'),
        ('light', 'Light'),
        ('weather', 'Weather'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    lamp = models.ForeignKey(Lamp, on_delete=models.CASCADE, related_name='sensors')


class SensorData(models.Model):
    id = models.BigAutoField(primary_key=True)  # Відповідає BIGSERIAL
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.JSONField()  # Для JSONB
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['sensor']),
        ]


class OutageSchedule(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='outages')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")


class EnergyConsumption(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(0)]
    )
    lamp = models.ForeignKey(Lamp, on_delete=models.CASCADE, related_name='energy_usage')

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['lamp']),
        ]


class Backup(models.Model):
    TYPE_CHOICES = [
        ('data', 'Data'),
        ('config', 'Config'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='backups')