"""
Custom filters for products and categories
"""
import django_filters
from django.db import models
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """Advanced product filtering"""
    
    # Price range filtering
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    price_range = django_filters.RangeFilter(field_name="price")
    
    # Category filtering
    category = django_filters.ModelChoiceFilter(
        field_name="categories",
        queryset=Category.objects.filter(is_active=True)
    )
    category_name = django_filters.CharFilter(
        field_name="categories__name", 
        lookup_expr='icontains'
    )
    
    # Stock filtering
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    # Seller filtering
    seller = django_filters.CharFilter(field_name="seller__username", lookup_expr='iexact')
    
    # Date filtering
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'is_featured': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products that are in stock"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (less than 10)"""
        if value:
            return queryset.filter(stock_quantity__lt=10, stock_quantity__gt=0)
        return queryset


class CategoryFilter(django_filters.FilterSet):
    """Category filtering"""
    
    name = django_filters.CharFilter(lookup_expr='icontains')
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Category
        fields = ['parent', 'is_active']
    
    def filter_has_products(self, queryset, name, value):
        """Filter categories that have products"""
        if value:
            return queryset.filter(products__isnull=False).distinct()
        return queryset.filter(products__isnull=True).distinct()