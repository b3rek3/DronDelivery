from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import Restaurant, MenuItem, CartItem, Order, OrderItem
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class BaseTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = APIClient()
        
        # Create test restaurant
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            description='Test Description',
            logo_path='test_logo.png',
            is_active=True
        )
        
        # Create test menu items
        self.menu_item1 = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Test Item 1',
            description='Test Description 1',
            price=10.99,
            image_path='test_image1.png'
        )
        self.menu_item2 = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Test Item 2',
            description='Test Description 2',
            price=15.99,
            image_path='test_image2.png'
        )

        # Test delivery location
        self.test_latitude = 43.1965135
        self.test_longitude = 76.6309754

    def create_test_order(self, user, status=Order.OrderStatus.CREATED):
        """Helper method to create a test order"""
        return Order.objects.create(
            user=user,
            restaurant=self.restaurant,
            total_price=Decimal('26.98'),
            delivery_latitude=self.test_latitude,
            delivery_longitude=self.test_longitude,
            status=status
        )

class UserViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin_user)
        self.url = reverse('user-list')

    def test_list_users(self):
        """Test listing all users (admin only)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # admin and test user

    def test_create_user(self):
        """Test creating a new user"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'budget': 1000.0
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_retrieve_user(self):
        """Test retrieving a specific user"""
        url = reverse('user-detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user(self):
        """Test updating a user"""
        url = reverse('user-detail', args=[self.user.id])
        data = {'first_name': 'Updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_user_stats(self):
        """Test retrieving user statistics"""
        order = self.create_test_order(self.user, Order.OrderStatus.COMPLETED)
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item1,
            quantity=2,
            price_at_time=self.menu_item1.price
        )

        url = reverse('user-stats', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 1)
        self.assertEqual(float(response.data['total_spent']), 26.98)

class RestaurantViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('restaurant-list')

    def test_list_restaurants(self):
        """Test listing all restaurants"""
        self.client.force_authenticate(user=self.user)  # Authenticate user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_restaurant(self):
        """Test creating a new restaurant (authenticated only)"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Restaurant',
            'description': 'New Description',
            'is_active': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 2)

    def test_retrieve_restaurant(self):
        """Test retrieving a specific restaurant"""
        url = reverse('restaurant-detail', args=[self.restaurant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Restaurant')

    def test_restaurant_menu(self):
        """Test retrieving restaurant menu"""
        url = reverse('restaurant-menu', args=[self.restaurant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_restaurant_stats(self):
        """Test retrieving restaurant statistics"""
        self.client.force_authenticate(user=self.user)
        order = self.create_test_order(self.user, Order.OrderStatus.COMPLETED)
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item1,
            quantity=2,
            price_at_time=self.menu_item1.price
        )

        url = reverse('restaurant-stats', args=[self.restaurant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 1)
        self.assertEqual(float(response.data['total_revenue']), 26.98)

class MenuItemViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('menuitem-list')
        self.client.force_authenticate(user=self.user)

    def test_list_menu_items(self):
        """Test listing all menu items"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_menu_item(self):
        """Test creating a new menu item (authenticated only)"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'restaurant': self.restaurant.id,
            'name': 'New Item',
            'description': 'New Description',
            'price': 20.99
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 3)

    def test_filter_by_restaurant(self):
        """Test filtering menu items by restaurant"""
        url = f"{self.url}?restaurant_id={self.restaurant.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_menu_items(self):
        """Test searching menu items"""
        response = self.client.get(f"{self.url}?search=Test Item 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Item 1')

class CartItemViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('cartitem-list')

    def test_list_cart_items(self):
        """Test listing user's cart items"""
        CartItem.objects.create(
            user=self.user,
            menu_item=self.menu_item1,
            quantity=2
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_cart_item(self):
        """Test creating a new cart item"""
        data = {
            'menu_item': self.menu_item1.id,
            'quantity': 2
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_update_cart_item(self):
        """Test updating a cart item"""
        cart_item = CartItem.objects.create(
            user=self.user,
            menu_item=self.menu_item1,
            quantity=2
        )
        url = reverse('cartitem-detail', args=[cart_item.id])
        data = {'quantity': 3}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

class OrderViewSetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('order-list')
        # Create cart items
        self.cart_item1 = CartItem.objects.create(
            user=self.user,
            menu_item=self.menu_item1,
            quantity=2
        )
        self.cart_item2 = CartItem.objects.create(
            user=self.user,
            menu_item=self.menu_item2,
            quantity=1
        )

    def test_create_order(self):
        """Test creating a new order from cart items"""
        data = {
            'delivery_latitude': self.test_latitude,
            'delivery_longitude': self.test_longitude
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 0)  # Cart should be cleared

    def test_list_orders(self):
        """Test listing user's orders"""
        self.create_test_order(self.user, Order.OrderStatus.CREATED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_order_status(self):
        """Test updating order status"""
        order = self.create_test_order(self.user, Order.OrderStatus.CREATED)
        url = reverse('order-detail', args=[order.id])
        data = {'status': Order.OrderStatus.IN_TRANSIT}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.IN_TRANSIT)

class DroneManagementTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.order = self.create_test_order(self.user, Order.OrderStatus.IN_TRANSIT)

    def test_drone_status(self):
        """Test retrieving drone status for an order"""
        url = reverse('drone-status', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_id'], self.order.id)
        self.assertEqual(response.data['status'], Order.OrderStatus.IN_TRANSIT)

    def test_drone_fleet(self):
        """Test retrieving drone fleet status (admin only)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('drone-fleet')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_drones', response.data)
        self.assertIn('available_drones', response.data)

class DeliveryManagementTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_weather_conditions(self):
        """Test retrieving weather conditions"""
        url = reverse('weather-condition')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('temperature', response.data)
        self.assertIn('is_safe_for_drone', response.data)

    def test_delivery_analytics(self):
        """Test retrieving delivery analytics (admin only)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('delivery-analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_deliveries', response.data)
        self.assertIn('successful_deliveries', response.data)
