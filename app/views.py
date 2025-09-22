"""
API Views for ALX Project Nexus
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Category, Product

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    CategorySerializer, ProductSerializer  
)
from .models import Category, Product  

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
            "register": "/api/auth/register/",
            "login": "/api/auth/login/",
            "refresh": "/api/auth/refresh/",
            "profile": "/api/auth/profile/",
        }
    })


class RegisterView(generics.CreateAPIView):
    """User registration"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
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
        
        # Generate tokens
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

class CategoryListView(generics.ListCreateAPIView):
    """List and create categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Allow anyone to view, but only authenticated users to create"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Category detail, update, delete"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow anyone to view, but only authenticated users to modify"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


class ProductListView(generics.ListCreateAPIView):
    """List and create products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'seller', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Allow anyone to view, but only sellers to create"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Ensure only sellers can create products"""
        if not self.request.user.is_seller:
            raise serializers.ValidationError("Only sellers can create products")
        serializer.save()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Product detail, update, delete"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow anyone to view, but only owner to modify"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_object(self):
        """Increment view count when product is viewed"""
        obj = super().get_object()
        if self.request.method == 'GET':
            obj.increment_view_count()
        return obj