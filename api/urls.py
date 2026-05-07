from django.urls import path, include
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, RegisterView, IoTDataReceiveView,
    AccountViewSet, DashboardViewSet, ZoneViewSet,
    LampViewSet, SensorViewSet, SensorDataViewSet,
    OutageScheduleViewSet, EnergyConsumptionViewSet, BackupViewSet, EnergyAnalyticsView, SystemHealthView
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'dashboards', DashboardViewSet)
router.register(r'zones', ZoneViewSet)
router.register(r'lamps', LampViewSet)
router.register(r'sensors', SensorViewSet)
router.register(r'sensor-data', SensorDataViewSet)
router.register(r'outage-schedules', OutageScheduleViewSet)
router.register(r'energy-consumption', EnergyConsumptionViewSet)
router.register(r'backups', BackupViewSet)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('iot/telemetry/', IoTDataReceiveView.as_view(), name = 'iot-telemetry'),
    path('analytics/<int:id>/', EnergyAnalyticsView.as_view(), name='energy-analytics'),
    path('admin/system-health/', SystemHealthView.as_view(), name='system-health'),
    path('', include(router.urls)),
    path('i18n/', include('django.conf.urls.i18n')),
]