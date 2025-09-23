"""
Category tests for ALX Project Nexus E-Commerce Backend
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Category

User = get_user_model()


class CategoryTestCase(TestCase):
    """Test category functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
    
    def test_list_categories_public(self):
        """Test anyone can view categories"""
        response = self.client.get('/api/categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
    
    def test_create_category_authenticated(self):
        """Test authenticated user can create category"""
        # Login first
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        token = login_response.data['tokens']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        data = {
            'name': 'Books',
            'description': 'Books and education'
        }
        
        response = self.client.post('/api/categories/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Books')
        self.assertEqual(response.data['slug'], 'books')
    
    def test_create_category_unauthenticated_fails(self):
        """Test unauthenticated user cannot create category"""
        data = {
            'name': 'Books',
            'description': 'Books and education'
        }
        
        response = self.client.post('/api/categories/', data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_search_categories(self):
        """Test category search"""
        response = self.client.get('/api/categories/?search=electronic')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)