"""
Django Admin Configuration for E-Commerce Models
ALX Project Nexus
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Category, Product, ProductImage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with additional e-commerce fields
    """
    # Fields to display in the user list
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_seller', 'is_staff', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'is_staff', 'is_active', 'is_seller', 
        'email_notifications', 'date_joined'
    ]
    
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
    
    # Organize fields in the user detail/edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('E-Commerce Profile', {
            'fields': (
                'phone_number', 'date_of_birth', 'profile_picture',
                'is_seller', 'email_notifications'
            )
        }),
        ('Address Information', {
            'fields': (
                'address_line1', 'address_line2', 'city', 
                'state', 'postal_code', 'country'
            ),
            'classes': ('collapse',)  # Collapsible section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed timestamps'
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    # Fields for add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'is_seller')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category Admin with hierarchical display
    """
    list_display = [
        'name', 'parent', 'product_count_display', 
        'is_active', 'display_order', 'created_at'
    ]
    
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Display Settings', {
            'fields': ('image', 'is_active', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def product_count_display(self, obj):
        """Display product count for this category"""
        count = obj.get_product_count()
        return f"{count} products"
    product_count_display.short_description = "Products"
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('parent')


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for product images
    """
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'display_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product Admin with comprehensive management
    """
    list_display = [
        'name', 'sku', 'seller', 'price', 'stock_quantity', 
        'is_active', 'is_featured', 'view_count', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'is_featured', 'track_inventory', 
        'categories', 'seller', 'created_at'
    ]
    
    search_fields = ['name', 'sku', 'description', 'seller__username']
    prepopulated_fields = {'slug': ('name',)}
    
    filter_horizontal = ['categories']  # Nice widget for many-to-many
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'seller')
        }),
        ('Product Details', {
            'fields': (
                'description', 'short_description', 
                'featured_image', 'categories'
            )
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price'),
            'description': 'Set pricing information'
        }),
        ('Inventory', {
            'fields': (
                'stock_quantity', 'track_inventory', 'allow_backorder'
            )
        }),
        ('Specifications', {
            'fields': (
                'weight', 'dimensions_length', 
                'dimensions_width', 'dimensions_height'
            ),
            'classes': ('collapse',)
        }),
        ('SEO & Visibility', {
            'fields': (
                'is_active', 'is_featured', 'meta_title', 'meta_description'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    inlines = [ProductImageInline]
    
    # Custom actions
    actions = ['make_active', 'make_inactive', 'make_featured']
    
    def make_active(self, request, queryset):
        """Bulk action to activate products"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products were activated.')
    make_active.short_description = "Mark selected products as active"
    
    def make_inactive(self, request, queryset):
        """Bulk action to deactivate products"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products were deactivated.')
    make_inactive.short_description = "Mark selected products as inactive"
    
    def make_featured(self, request, queryset):
        """Bulk action to feature products"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products were marked as featured.')
    make_featured.short_description = "Mark selected products as featured"
    
    def get_queryset(self, request):
        """Optimize queries with select_related and prefetch_related"""
        return super().get_queryset(request).select_related(
            'seller'
        ).prefetch_related('categories')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Product Image Admin
    """
    list_display = ['product', 'alt_text', 'display_order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'alt_text']
    
    fieldsets = (
        (None, {
            'fields': ('product', 'image', 'alt_text', 'display_order')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


# Customize admin site header and title
admin.site.site_header = "ALX Project Nexus - E-Commerce Admin"
admin.site.site_title = "E-Commerce Admin"
admin.site.index_title = "Welcome to E-Commerce Administration"