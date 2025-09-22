"""
E-Commerce Backend Models
ALX Project Nexus
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from PIL import Image
import uuid
import os


class User(AbstractUser):
    """
    Custom User model with additional e-commerce fields
    """
    # Additional fields for e-commerce
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        help_text="Profile picture (optional)"
    )
    
    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default='South Africa')
    
    # User preferences
    is_seller = models.BooleanField(default=False, help_text="Can this user sell products?")
    email_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name(self):
        """Return full name or username if names are not provided"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def save(self, *args, **kwargs):
        """Override save to resize profile pictures"""
        super().save(*args, **kwargs)
        
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class Category(models.Model):
    """
    Product Category model with hierarchical support
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    # Hierarchical categories (subcategories)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    
    # Category image
    image = models.ImageField(
        upload_to='category_images/', 
        blank=True, 
        null=True,
        help_text="Category banner image"
    )
    
    # SEO and display
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Order for displaying categories")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name"""
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_all_children(self):
        """Get all subcategories recursively"""
        children = []
        for child in self.subcategories.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_product_count(self):
        """Get total number of products in this category and subcategories"""
        count = self.products.filter(is_active=True).count()
        for child in self.subcategories.all():
            count += child.get_product_count()
        return count


class Product(models.Model):
    """
    Product model for e-commerce catalog
    """
    # Product identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit")
    
    # Product details
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    compare_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Original price for discount display"
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Cost price for profit calculation"
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    
    # Product specifications
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    dimensions_length = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Length in cm")
    dimensions_width = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Width in cm")
    dimensions_height = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Height in cm")
    
    # Relationships
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    
    # Product images
    featured_image = models.ImageField(
        upload_to='product_images/', 
        blank=True, 
        null=True,
        help_text="Main product image"
    )
    
    # SEO and visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=60, blank=True, null=True)
    meta_description = models.CharField(max_length=160, blank=True, null=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['seller']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['stock_quantity']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and SKU"""
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if not self.sku:
            # Generate SKU: first 3 letters of name + random number
            name_part = ''.join(c for c in self.name if c.isalpha())[:3].upper()
            random_part = str(uuid.uuid4().int)[:6]
            self.sku = f"{name_part}-{random_part}"
            
            # Ensure unique SKU
            counter = 1
            original_sku = self.sku
            while Product.objects.filter(sku=self.sku).exclude(pk=self.pk).exists():
                self.sku = f"{original_sku}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price is set"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    @property
    def profit_margin(self):
        """Calculate profit margin if cost_price is set"""
        if self.cost_price and self.cost_price > 0:
            return round(((self.price - self.cost_price) / self.price) * 100, 2)
        return 0
    
    def increment_view_count(self):
        """Increment product view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ProductImage(models.Model):
    """
    Additional product images
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order', 'created_at']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Image {self.display_order + 1}"
    
    def save(self, *args, **kwargs):
        """Resize image and set alt_text if not provided"""
        if not self.alt_text:
            self.alt_text = f"{self.product.name} image"
        
        super().save(*args, **kwargs)
        
        # Resize image
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)