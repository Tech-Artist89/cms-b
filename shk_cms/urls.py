"""
URL configuration for SHK-CMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/v1/', include('shk_cms.api.urls')),
    path('api/v1/auth/', include('shk_cms.core.urls')),
    path('api/v1/customers/', include('shk_cms.customers.urls')),
    path('api/v1/projects/', include('shk_cms.projects.urls')),
    path('api/v1/quotes/', include('shk_cms.quotes.urls')),
    path('api/v1/invoices/', include('shk_cms.invoices.urls')),
    path('api/v1/employees/', include('shk_cms.employees.urls')),
    path('api/v1/timetracking/', include('shk_cms.timetracking.urls')),
    path('api/v1/schedules/', include('shk_cms.schedules.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "SHK-CMS Administration"
admin.site.site_title = "SHK-CMS Admin"
admin.site.index_title = "Willkommen im SHK-CMS"