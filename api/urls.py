from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, RegisterView, IoTDataReceiveView,
    AccountViewSet, DashboardViewSet, ZoneViewSet,
    LampViewSet, SensorViewSet, SensorDataViewSet,
    OutageScheduleViewSet, EnergyConsumptionViewSet, BackupViewSet
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
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('iot/data/', IoTDataReceiveView.as_view(), name='iot-data-receive'),
    path('', include(router.urls)),
]