"""
API Views for ALX Project Nexus
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    CategorySerializer, ProductSerializer
)
from .models import Category, Product
from .filters import ProductFilter, CategoryFilter

User = get_user_model()


def home_view(request):
    """Homepage view for the root URL"""
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


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint"""
    return Response({
        "message": "ALX Project Nexus - E-Commerce API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "refresh": "/api/auth/refresh/",
                "profile": "/api/auth/profile/",
            },
            "catalog": {
                "categories": "/api/categories/",
                "products": "/api/products/",
                "search": "/api/products/?search=keyword",
                "filter": "/api/products/?min_price=100&max_price=500",
            }
        }
    })


# Authentication views 
class RegisterView(generics.CreateAPIView):
    """User registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


# Enhanced Category views
class CategoryListView(generics.ListCreateAPIView):
    """List and create categories with filtering"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Category detail, update, delete"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


# Enhanced Product views
class ProductListView(generics.ListCreateAPIView):
    """List and create products with advanced filtering"""
    queryset = Product.objects.filter(is_active=True).select_related('seller').prefetch_related('categories')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'view_count', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        if not self.request.user.is_seller:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only sellers can create products")
        serializer.save()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Product detail, update, delete"""
    queryset = Product.objects.select_related('seller').prefetch_related('categories')
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_object(self):
        obj = super().get_object()
        if self.request.method == 'GET':
            obj.increment_view_count()
        return obj