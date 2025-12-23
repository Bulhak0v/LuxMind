from django.contrib import admin
from .models import *

@admin.register(Lamp)
class LampAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'zone', 'status', 'current_brightness')
    list_filter = ('status', 'zone')

admin.site.register(Account)
admin.site.register(Dashboard)
admin.site.register(Zone)
admin.site.register(Sensor)
admin.site.register(SensorData)
admin.site.register(OutageSchedule)
admin.site.register(EnergyConsumption)
admin.site.register(Backup)