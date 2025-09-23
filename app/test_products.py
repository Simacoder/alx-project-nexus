"""
Product tests for ALX Project Nexus E-Commerce Backend
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Category, Product

User = get_user_model()


class ProductTestCase(TestCase):
    """Test product functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create users
        self.seller = User.objects.create_user(
            username='seller',
            password='sellerpass123',
            is_seller=True
        )
        self.regular_user = User.objects.create_user(
            username='buyer',
            password='buyerpass123',
            is_seller=False
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        
        # Create product
        self.product = Product.objects.create(
            name='iPhone 15',
            description='Latest iPhone',
            price='15999.99',
            stock_quantity=10,
            seller=self.seller,
            is_featured=True
        )
        self.product.categories.add(self.category)
    
    def get_token(self, user):
        """Helper to get auth token"""
        response = self.client.post('/api/auth/login/', {
            'username': user.username,
            'password': f'{user.username}pass123'
        })
        return response.data['tokens']['access']
    
    def test_list_products_public(self):
        """Test anyone can view products"""
        response = self.client.get('/api/products/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'iPhone 15')
    
    def test_create_product_as_seller(self):
        """Test seller can create product"""
        token = self.get_token(self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'New Product',
            'description': 'A great product',
            'price': '99.99',
            'stock_quantity': 20,
            'category_ids': [self.category.id]
        }
        
        response = self.client.post('/api/products/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')
        self.assertEqual(response.data['seller'], self.seller.id)
    
    def test_create_product_as_regular_user_fails(self):
        """Test regular user cannot create product"""
        token = self.get_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'New Product',
            'description': 'A great product',
            'price': '99.99',
            'stock_quantity': 20
        }
        
        response = self.client.post('/api/products/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_search_products(self):
        """Test product search"""
        response = self.client.get('/api/products/?search=iphone')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'iPhone 15')
    
    def test_filter_by_price(self):
        """Test price filtering"""
        # Should find iPhone (expensive)
        response = self.client.get('/api/products/?min_price=10000')
        self.assertEqual(response.data['count'], 1)
        
        # Should find nothing (too expensive)
        response = self.client.get('/api/products/?max_price=100')
        self.assertEqual(response.data['count'], 0)
    
    def test_filter_featured(self):
        """Test featured products filter"""
        response = self.client.get('/api/products/?is_featured=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'iPhone 15')
    
    def test_sort_by_price(self):
        """Test sorting by price"""
        # Create cheaper product
        Product.objects.create(
            name='Cheap Phone',
            price='99.99',
            stock_quantity=5,
            seller=self.seller
        )
        
        # Sort ascending
        response = self.client.get('/api/products/?ordering=price')
        prices = [float(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices))
        
        # Sort descending  
        response = self.client.get('/api/products/?ordering=-price')
        prices = [float(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))