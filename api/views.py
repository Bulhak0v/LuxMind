from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q, Sum, Avg
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import *
from .serializers import *
from .services import LightingService, AdminService


class LoginView(APIView):
    @extend_schema(request=LoginRequestSerializer, responses={200: LoginResponseSerializer})
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = Account.objects.get(
                    username=serializer.validated_data['username'],
                    password_hash=serializer.validated_data['password']
                )
                return Response({
                    "token": "simulated_jwt_token_for_lab_3",
                    "id": user.id,
                    "role": user.role
                }, status=status.HTTP_200_OK)
            except Account.DoesNotExist:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    @extend_schema(
        request=AccountSerializer,
        responses={201: RegisterResponseSerializer},
        description="Реєстрація нового облікового запису."
    )
    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IoTDataReceiveView(APIView):
    @extend_schema(
        request=IoTTelemetrySerializer,
        responses={200: dict},
        description="Прийом телеметрії від IoT-пристрою та отримання команд керування."
    )
    def post(self, request):
        serializer = IoTTelemetrySerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            motion_level = serializer.validated_data['motion_level']
            consumption = serializer.validated_data['consumption']
            ambient_light = request.data.get('ambient_light', 0)

            try:
                result = LightingService.process_iot_telemetry(
                    id, motion_level, consumption, ambient_light
                )
                return Response(result, status=status.HTTP_200_OK)
            except Lamp.DoesNotExist:
                return Response({"error": "Lamp not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnergyAnalyticsView(APIView):
    @extend_schema(
        responses={200: EnergyAnalyticsSerializer},
        description="Отримання статистики енергоефективності дашборду."
    )
    def get(self, request, id):
        stats = LightingService.get_energy_savings(id)
        return Response(stats, status=status.HTTP_200_OK)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role')
        if role:
            return self.queryset.filter(role=role)
        return self.queryset


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    def get_queryset(self):
        id = self.request.query_params.get('id')
        return self.queryset.filter(account_id=id) if id else self.queryset


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    def get_queryset(self):
        id = self.request.query_params.get('id')
        return self.queryset.filter(dashboard_id=id) if id else self.queryset


class LampViewSet(viewsets.ModelViewSet):
    queryset = Lamp.objects.all()
    serializer_class = LampSerializer
    def get_queryset(self):
        id = self.request.query_params.get('id')
        return self.queryset.filter(zone_id=id) if id else self.queryset

    @action(detail=False, methods=['post'])
    def bulk_status_update(self, request):
        ids = request.data.get('ids', [])
        updated = Lamp.objects.filter(id__in=ids).update(status=request.data.get('status'))
        return Response({"message": f"Updated {updated} lamps"})


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    def get_queryset(self):
        id = self.request.query_params.get('id')
        return self.queryset.filter(lamp_id=id) if id else self.queryset


class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        sensor_id = self.request.query_params.get('sensor_id')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        qs = self.queryset
        if sensor_id: qs = qs.filter(sensor_id=sensor_id)
        if start_time and end_time:
            qs = qs.filter(timestamp__range=[start_time, end_time])
        return qs.order_by('-timestamp')


class OutageScheduleViewSet(viewsets.ModelViewSet):
    queryset = OutageSchedule.objects.all()
    serializer_class = OutageScheduleSerializer

    def get_queryset(self):
        is_active = self.request.query_params.get('active')
        if is_active == 'true':
            now = timezone.now()
            return self.queryset.filter(start_time__lte=now, end_time__gte=now)
        return self.queryset


class EnergyConsumptionViewSet(viewsets.ModelViewSet):
    queryset = EnergyConsumption.objects.all()
    serializer_class = EnergyConsumptionSerializer

    def get_queryset(self):
        lamp_id = self.request.query_params.get('lamp_id')
        if lamp_id:
            return self.queryset.filter(lamp_id=lamp_id)
        return self.queryset

    @action(detail=False, methods=['get'])
    def total_stats(self, request):
        total = self.get_queryset().aggregate(Sum('amount_kwh'))
        return Response({'total_consumption_kwh': total['amount_kwh__sum'] or 0})


class SystemHealthView(APIView):
    @extend_schema(
        responses={200: SystemHealthSerializer},
        description="Звіт про загальний стан інфраструктури (для адміна)."
    )
    def get(self, request):
        report = AdminService.get_system_health_report()
        return Response(report, status=status.HTTP_200_OK)


class BackupViewSet(viewsets.ModelViewSet):
    queryset = Backup.objects.all()
    serializer_class = BackupSerializer
    def get_queryset(self):
        id = self.request.query_params.get('id')
        return self.queryset.filter(account_id=id) if id else self.queryset

    def create(self, request, *args, **kwargs):
        id = request.data.get('id')
        backup = AdminService.create_system_backup(id, request.data.get('type', 'data'))
        return Response(BackupSerializer(backup).data, status=status.HTTP_201_CREATED)
