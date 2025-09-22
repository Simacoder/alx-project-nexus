"""
URLs for the app
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import views
from . import views

# API endpoints
urlpatterns = [
    # API root
    path('', views.api_root, name='api-root'),
    
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
]

# We might use routers for ViewSets later
router = DefaultRouter()
# router.register('products', ProductViewSet)
# router.register('categories', CategoryViewSet)

urlpatterns += router.urls

