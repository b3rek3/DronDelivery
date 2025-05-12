from rest_framework import serializers
from core.models import User, Restaurant, MenuItem, CartItem, Order, OrderItem
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name', 'budget', 'created_at')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'budget')

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'description', 'logo_path')

class MenuItemSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = ('id', 'restaurant', 'restaurant_name', 'name', 'description', 'price', 'image_path')

class CartItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'menu_item', 'menu_item_details', 'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.menu_item.price * obj.quantity

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'menu_item_details', 'quantity', 'price_at_time', 'subtotal')

    def get_subtotal(self, obj):
        return obj.price_at_time * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'user_details', 'restaurant', 'restaurant_details', 
                 'total_price', 'delivery_latitude', 'delivery_longitude', 
                 'status', 'status_display', 'created_at', 'items')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('delivery_latitude', 'delivery_longitude')

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

class DroneStatusSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.CharField()
    battery_level = serializers.IntegerField()
    current_latitude = serializers.FloatField()
    current_longitude = serializers.FloatField()
    estimated_arrival_time = serializers.DateTimeField()

class RestaurantStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_revenue = serializers.FloatField()
    average_order_value = serializers.FloatField()
    popular_items = MenuItemSerializer(many=True)
    menu_item_count = serializers.IntegerField()
    active_orders = serializers.IntegerField()

class UserStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_spent = serializers.FloatField()
    favorite_restaurants = RestaurantSerializer(many=True)
    recent_orders = OrderSerializer(many=True)

class WeatherConditionSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    wind_speed = serializers.FloatField()
    precipitation = serializers.FloatField()
    visibility = serializers.FloatField()
    is_safe_for_drone = serializers.BooleanField()

class DroneFleetSerializer(serializers.Serializer):
    total_drones = serializers.IntegerField()
    available_drones = serializers.IntegerField()
    active_deliveries = serializers.IntegerField()
    maintenance_drones = serializers.IntegerField()
    average_battery_level = serializers.FloatField()

class DeliveryAnalyticsSerializer(serializers.Serializer):
    total_deliveries = serializers.IntegerField()
    successful_deliveries = serializers.IntegerField()
    average_delivery_time = serializers.FloatField()
    peak_delivery_hours = serializers.ListField(child=serializers.IntegerField())
    popular_delivery_zones = serializers.ListField(child=serializers.DictField()) 