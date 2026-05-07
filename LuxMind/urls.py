from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path, include  # ОЦЬОГО РЯДКА ВАС НЕ ВИСТАЧАЄ
from django.conf.urls.i18n import *
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),

    # OpenAPI схема
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Фронтенд (Auth SPA, Operator SPA, Admin SPA)
    path('', TemplateView.as_view(template_name='auth.html'), name='auth_page'),
    path('operator-app/', TemplateView.as_view(template_name='operator.html'), name='operator_page'),
    path('admin-app/', TemplateView.as_view(template_name='admin.html'), name='admin_page'),
    path('i18n/', include('django.conf.urls.i18n')),
]