"""
Main API URL configuration
"""

from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

app_name = 'api'


@api_view(['GET'])
def api_root(request):
    """
    API Root endpoint
    """
    return Response({
        'message': 'SHK-CMS API v1.0',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'customers': '/api/v1/customers/',
            'projects': '/api/v1/projects/',
            'quotes': '/api/v1/quotes/',
            'invoices': '/api/v1/invoices/',
            'employees': '/api/v1/employees/',
            'timetracking': '/api/v1/timetracking/',
            'schedules': '/api/v1/schedules/',
            'docs': '/api/docs/',
        }
    })


urlpatterns = [
    path('', api_root, name='api_root'),
]