from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Account, Dashboard, Zone, Lamp, Sensor,
    SensorData, OutageSchedule, EnergyConsumption, Backup
)
from .serializers import (
    AccountSerializer, DashboardSerializer, ZoneSerializer,
    LampSerializer, SensorSerializer, SensorDataSerializer,
    OutageScheduleSerializer, EnergyConsumptionSerializer, BackupSerializer
)

class LoginView(APIView):
    def post(self, request):
        # Бізнес-логіка (перевірка пароля, видача JWT) — реалізується в ЛР №3
        return Response({"detail": "Not implemented yet (ЛР №3)"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class RegisterView(APIView):
    def post(self, request):
        return Response({"detail": "Not implemented yet (ЛР №3)"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class IoTDataReceiveView(APIView):
    def post(self, request):
        # Прийом даних з IoT, повернення команд — ЛР №3
        return Response({"detail": "IoT data endpoint ready (ЛР №3)"}, status=status.HTTP_501_NOT_IMPLEMENTED)

# Стандартні CRUD ViewSets
class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

class LampViewSet(viewsets.ModelViewSet):
    queryset = Lamp.objects.all()
    serializer_class = LampSerializer

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer

class OutageScheduleViewSet(viewsets.ModelViewSet):
    queryset = OutageSchedule.objects.all()
    serializer_class = OutageScheduleSerializer

class EnergyConsumptionViewSet(viewsets.ModelViewSet):
    queryset = EnergyConsumption.objects.all()
    serializer_class = EnergyConsumptionSerializer

class BackupViewSet(viewsets.ModelViewSet):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer