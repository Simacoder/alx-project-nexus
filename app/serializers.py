"""
Serializers for authentication
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Category, Product

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_seller', 'phone_number', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """User registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'is_seller']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """User login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                data['user'] = user
                return data
            raise serializers.ValidationError("Invalid credentials")
        raise serializers.ValidationError("Must provide username and password")
    

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 
                 'is_active', 'product_count', 'created_at']
        read_only_fields = ['slug', 'created_at']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'sku', 'description', 'price', 
                 'stock_quantity', 'seller', 'seller_name', 'categories', 
                 'category_ids', 'is_active', 'is_featured', 'created_at']
        read_only_fields = ['id', 'slug', 'sku', 'seller', 'created_at']
    
    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        validated_data['seller'] = self.context['request'].user
        product = Product.objects.create(**validated_data)
        
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            product.categories.set(categories)
        
        return product