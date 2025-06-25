from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Category, Review  

User = get_user_model()

class ProductReviewTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='A test product',
            price=50.00,
            quantity=10
        )
        self.client = APIClient()

    def test_product_list(self):
        url = reverse('product-list-create')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)

    def test_review_list_and_create(self):
        url = reverse('review-list')  

        # Test listing reviews (empty initially)
        response = self.client.get(url, {'product': self.product.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0) 

        # Authenticate user and create review
        self.client.force_authenticate(user=self.user)
        review_data = {
            'product': self.product.id,
            'rating': 5,
            'comment': 'Excellent product!'
        }
        response = self.client.post(url, review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Excellent product!')


class CartTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='A test product',
            price=99.99,
            quantity=10
        )
        self.client = APIClient()

    def test_get_cart_empty(self):
        url = reverse('cart') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart_items'], [])
        self.assertEqual(response.data['total_price'], 0)

    def test_add_product_to_cart(self):
        url = reverse('cart')
        self.client.force_authenticate(user=self.user)
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Verify item is in cart
        response = self.client.get(url)
        self.assertEqual(len(response.data['cart_items']), 1)
        self.assertEqual(response.data['cart_items'][0]['quantity'], 2)

    def test_delete_product_from_cart(self):
        url = reverse('cart')
        self.client.force_authenticate(user=self.user)
        # Add product first
        self.client.post(url, {'product_id': self.product.id, 'quantity': 1}, format='json')
        # Delete product
        response = self.client.delete(url, {'product_id': self.product.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Confirm cart is empty
        response = self.client.get(url)
        self.assertEqual(len(response.data['cart_items']), 0)
