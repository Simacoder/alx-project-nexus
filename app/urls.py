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

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]

# We might use routers for ViewSets later
router = DefaultRouter()
# router.register('products', ProductViewSet)
# router.register('categories', CategoryViewSet)

urlpatterns += router.urls

