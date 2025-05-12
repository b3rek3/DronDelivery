from django.shortcuts import render
from rest_framework import viewsets, status, permissions, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from core.models import User, Restaurant, MenuItem, CartItem, Order, OrderItem
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import (
    UserSerializer, UserUpdateSerializer, RestaurantSerializer, MenuItemSerializer,
    CartItemSerializer, OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    DroneStatusSerializer, RestaurantStatsSerializer, UserStatsSerializer,
    WeatherConditionSerializer, DroneFleetSerializer, DeliveryAnalyticsSerializer
)

# Create your views here.

# User Management
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'id']
    ordering = ['username']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                description='Search users by username, email, or name'
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with "-" for descending)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        user = self.get_object()
        orders = Order.objects.filter(user=user)
        
        stats = {
            'total_orders': orders.count(),
            'total_spent': orders.aggregate(total=Sum('total_price'))['total'] or 0,
            'favorite_restaurants': Restaurant.objects.filter(
                orders__user=user
            ).annotate(
                order_count=Count('orders')
            ).order_by('-order_count')[:5],
            'recent_orders': orders.order_by('-created_at')[:5]
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)

# Restaurant Management
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                description='Search restaurants by name or description'
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with "-" for descending)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def menu(self, request, pk=None):
        restaurant = self.get_object()
        menu_items = MenuItem.objects.filter(restaurant=restaurant)
        serializer = MenuItemSerializer(menu_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        restaurant = self.get_object()
        orders = Order.objects.filter(restaurant=restaurant)
        
        stats = {
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(total=Sum('total_price'))['total'] or 0,
            'average_order_value': orders.aggregate(avg=Avg('total_price'))['avg'] or 0,
            'popular_items': MenuItem.objects.filter(
                order_items__order__restaurant=restaurant
            ).annotate(
                order_count=Count('order_items')
            ).order_by('-order_count')[:5],
            'menu_item_count': MenuItem.objects.filter(restaurant=restaurant).count(),
            'active_orders': orders.filter(status=Order.OrderStatus.IN_TRANSIT).count()
        }
        
        serializer = RestaurantStatsSerializer(stats)
        return Response(serializer.data)

# Menu Item Management
class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'restaurant__name']
    ordering_fields = ['name', 'price', 'id']
    ordering = ['name']

    def get_queryset(self):
        queryset = MenuItem.objects.select_related('restaurant').all()
        restaurant_id = self.request.query_params.get('restaurant_id', None)
        if restaurant_id is not None:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                type=str,
                description='Search menu items by name, description, or restaurant name'
            ),
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with "-" for descending)'
            ),
            OpenApiParameter(
                name='restaurant_id',
                type=int,
                description='Filter by restaurant ID'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

# Cart Management
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'id']
    ordering = ['-created_at']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with "-" for descending)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Order Management
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'status', 'total_price', 'id']
    ordering = ['-created_at']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=str,
                description='Order by field (prefix with "-" for descending)'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty")
        
        restaurant = cart_items.first().menu_item.restaurant
        total = sum(item.menu_item.price * item.quantity for item in cart_items)
        
        order = serializer.save(
            user=self.request.user,
            restaurant=restaurant,
            total_price=total,
            status=Order.OrderStatus.CREATED
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price_at_time=cart_item.menu_item.price
            )
        
        # Clear cart
        cart_items.delete()
        return order

# Drone Management
class DroneStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Simulate drone status (in a real app, this would come from drone telemetry)
        status_data = {
            'order_id': order.id,
            'status': order.status,
            'battery_level': 85,  # Simulated
            'current_latitude': 43.1965135,  # Simulated
            'current_longitude': 76.6309754,  # Simulated
            'estimated_arrival_time': timezone.now() + timedelta(minutes=15)  # Simulated
        }
        
        serializer = DroneStatusSerializer(status_data)
        return Response(serializer.data)

class DroneFleetView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Simulate fleet status (in a real app, this would come from drone management system)
        fleet_data = {
            'total_drones': 10,
            'available_drones': 7,
            'active_deliveries': 3,
            'maintenance_drones': 0,
            'average_battery_level': 78.5
        }
        
        serializer = DroneFleetSerializer(fleet_data)
        return Response(serializer.data)

# Delivery Management
class WeatherConditionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Simulate weather conditions (in a real app, this would come from weather API)
        weather_data = {
            'temperature': 22.5,
            'wind_speed': 5.2,
            'precipitation': 0.0,
            'visibility': 10.0,
            'is_safe_for_drone': True
        }
        
        serializer = WeatherConditionSerializer(weather_data)
        return Response(serializer.data)

class DeliveryAnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Calculate delivery analytics
        orders = Order.objects.all()
        successful_deliveries = orders.filter(status=Order.OrderStatus.COMPLETED)
        
        analytics_data = {
            'total_deliveries': orders.count(),
            'successful_deliveries': successful_deliveries.count(),
            'average_delivery_time': 25.5,  # Simulated
            'peak_delivery_hours': [12, 13, 18, 19],  # Simulated
            'popular_delivery_zones': [
                {'latitude': 43.1965135, 'longitude': 76.6309754, 'count': 150},
                {'latitude': 43.2000000, 'longitude': 76.6500000, 'count': 120}
            ]
        }
        
        serializer = DeliveryAnalyticsSerializer(analytics_data)
        return Response(serializer.data)
