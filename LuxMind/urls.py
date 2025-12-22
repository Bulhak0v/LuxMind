from django.contrib import admin
from django.urls import path, include  # ОЦЬОГО РЯДКА ВАС НЕ ВИСТАЧАЄ
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),

    # OpenAPI схема
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI — найкращий варіант для звіту
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc — альтернативний стиль
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]