"""
Authentication tests for ALX Project Nexus E-Commerce Backend
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class AuthTestCase(TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test'
        }
        
        # Create existing user for login tests
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='existingpass123'
        )
    
    def test_register_user_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_register_password_mismatch(self):
        """Test registration with password mismatch"""
        data = self.user_data.copy()
        data['password_confirm'] = 'different'
        
        response = self.client.post('/api/auth/register/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        """Test successful login"""
        login_data = {
            'username': 'existing',
            'password': 'existingpass123'
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        login_data = {
            'username': 'existing',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_profile_authenticated(self):
        """Test getting profile when authenticated"""
        # Get tokens
        login_response = self.client.post('/api/auth/login/', {
            'username': 'existing',
            'password': 'existingpass123'
        })
        token = login_response.data['tokens']['access']
        
        # Use token to get profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existing')
    
    def test_profile_unauthenticated(self):
        """Test profile endpoint without authentication"""
        response = self.client.get('/api/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)