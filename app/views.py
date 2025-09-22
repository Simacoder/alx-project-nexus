from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Welcome message and available endpoints
    """
    return Response({
        "message": "Welcome to ALX Project Nexus - E-Commerce Backend API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api_docs_swagger": "/swagger/",
            "api_docs_redoc": "/redoc/",
            "api": "/api/",
        },
        "status": "Development"
    })

def home_view(request):
    """
    Simple homepage redirect
    """
    return JsonResponse({
        "project": "ALX Project Nexus - E-Commerce Backend",
        "message": "Welcome! Visit /swagger/ for API documentation",
        "available_urls": {
            "admin": "/admin/",
            "swagger": "/swagger/",
            "redoc": "/redoc/",
            "api": "/api/"
        }
    })