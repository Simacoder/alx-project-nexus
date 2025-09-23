"""
documented API Views for ALX Project Nexus E-Commerce Backend
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model, models
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    CategorySerializer, ProductSerializer
)
from .models import Category, Product
from .filters import ProductFilter, CategoryFilter

User = get_user_model()


def home_view(request):
    """
    Homepage view returning project information
    
    Returns basic project info and navigation links
    for users visiting the root URL.
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


@swagger_auto_schema(
    method='get',
    operation_description="Get API overview and available endpoints",
    responses={200: "API information"}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root Endpoint
    
    Provides an overview of all available API endpoints
    and their purposes. Great starting point for API exploration.
    """
    return Response({
        "message": "ALX Project Nexus - E-Commerce API",
        "version": "1.0.0",
        "documentation": "/swagger/",
        "endpoints": {
            "authentication": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/", 
                "refresh_token": "/api/auth/refresh/",
                "profile": "/api/auth/profile/",
            },
            "catalog": {
                "categories": "/api/categories/",
                "products": "/api/products/",
            },
            "filtering_examples": {
                "search": "/api/products/?search=keyword",
                "price_range": "/api/products/?min_price=100&max_price=500",
                "category": "/api/products/?category=1",
                "in_stock": "/api/products/?in_stock=true",
                "sort_by_price": "/api/products/?ordering=price",
            }
        }
    })


class RegisterView(generics.CreateAPIView):
    """
    User Registration Endpoint
    
    Creates a new user account and returns JWT tokens for immediate login.
    New users can optionally register as sellers to create products.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="""
        Register a new user account
        
        Creates a new user and automatically generates JWT tokens.
        Set is_seller=true if the user wants to sell products.
        """,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "newuser",
                            "email": "user@example.com",
                            "is_seller": False
                        },
                        "tokens": {
                            "access": "jwt_access_token_here",
                            "refresh": "jwt_refresh_token_here"
                        }
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    User Login Endpoint
    
    Authenticates user credentials and returns JWT tokens.
    Supports login with either username or email.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="""
        Authenticate user and return JWT tokens
        
        Accepts username or email with password.
        Returns access token (1 hour) and refresh token (7 days).
        """,
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "testuser",
                            "email": "user@example.com"
                        },
                        "tokens": {
                            "access": "jwt_access_token_here",
                            "refresh": "jwt_refresh_token_here"
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid credentials"
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate fresh JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile Management
    
    Allows authenticated users to view and update their profile information.
    Supports partial updates (PATCH) for individual fields.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user"""
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Get current user profile information",
        responses={200: UserSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update user profile (supports partial updates)",
        responses={
            200: UserSerializer,
            400: "Bad Request - Validation errors"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CategoryListView(generics.ListCreateAPIView):
    """
    Category Management
    
    List all active categories with optional filtering and search.
    Authenticated users can create new categories.
    """
    queryset = Category.objects.filter(is_active=True).prefetch_related('products')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Allow anyone to view, authenticated users to create"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="""
        List categories with filtering and search
        
        Supports:
        - Search: ?search=electronics
        - Ordering: ?ordering=name or ?ordering=-created_at
        - Filter by parent: ?parent=1
        - Filter categories with products: ?has_products=true
        """,
        responses={200: CategorySerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new category (requires authentication)",
        responses={
            201: CategorySerializer,
            400: "Bad Request - Validation errors",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProductListView(generics.ListCreateAPIView):
    """
    Product Catalog Management
    
    Comprehensive product listing with advanced filtering, search, and sorting.
    Only sellers can create new products.
    """
    queryset = Product.objects.filter(is_active=True).select_related('seller').prefetch_related('categories')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'view_count', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Allow anyone to view, authenticated sellers to create"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="""
        List products with comprehensive filtering and search
        
        Available filters:
        - Price: ?min_price=100&max_price=500
        - Category: ?category=1 or ?category_name=electronics
        - Stock: ?in_stock=true or ?low_stock=true
        - Seller: ?seller=username
        - Featured: ?is_featured=true
        - Search: ?search=iphone (searches name, description, SKU)
        - Sort: ?ordering=price or ?ordering=-price
        
        Combine multiple filters: ?search=phone&min_price=1000&in_stock=true&ordering=-price
        """,
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="""
        Create a new product (sellers only)
        
        Only users with is_seller=true can create products.
        The seller field is automatically set to the authenticated user.
        """,
        responses={
            201: ProductSerializer,
            400: "Bad Request - Validation errors",
            401: "Authentication required",
            403: "Permission denied - Only sellers can create products"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Validate seller permissions and save product"""
        if not self.request.user.is_seller:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only sellers can create products. Set is_seller=true in your profile.")
        serializer.save()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Individual Product Management
    
    View, update, or delete specific products by slug.
    Automatically tracks view count for analytics.
    """
    queryset = Product.objects.select_related('seller').prefetch_related('categories')
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow anyone to view, authenticated users to modify their own products"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="""
        Get product details by slug
        
        Automatically increments view_count for analytics.
        Returns full product information including categories and seller details.
        """,
        responses={
            200: ProductSerializer,
            404: "Product not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        """Get product and increment view count for GET requests"""
        obj = super().get_object()
        if self.request.method == 'GET':
            # Increment view count for analytics (non-blocking)
            Product.objects.filter(pk=obj.pk).update(
                view_count=models.F('view_count') + 1
            )
            obj.refresh_from_db()
        return obj
    

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Category Detail Management
    
    View, update, or delete individual categories by slug.
    Anyone can view, but only authenticated users can modify.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow anyone to view, authenticated users to modify"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Get category details by slug",
        responses={
            200: CategorySerializer,
            404: "Category not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update category (requires authentication)",
        responses={
            200: CategorySerializer,
            400: "Bad Request - Validation errors",
            401: "Authentication required",
            404: "Category not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update category (requires authentication)",
        responses={
            200: CategorySerializer,
            400: "Bad Request - Validation errors", 
            401: "Authentication required",
            404: "Category not found"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete category (requires authentication)",
        responses={
            204: "Category deleted successfully",
            401: "Authentication required",
            404: "Category not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)