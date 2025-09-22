"""
URLs for the main app
"""
"""
URLs for the main app
"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# API endpoints
urlpatterns = [
    # API Root
    path('', views.api_root, name='api-root'),
    
    # Authentication URLs (will add in Phase 2)
    # Product URLs (will add in Phase 3)
    # Category URLs (will add in Phase 3)
]

# We might use routers for ViewSets later
router = DefaultRouter()
# router.register('products', ProductViewSet)
# router.register('categories', CategoryViewSet)

urlpatterns += router.urls