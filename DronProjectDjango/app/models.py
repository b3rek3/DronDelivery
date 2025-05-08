from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    budget   = models.FloatField(default=1000.0)

class Restaurant(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo        = models.ImageField(upload_to='logos/', blank=True)

class MenuItem(models.Model):
    restaurant    = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    price         = models.FloatField()
    image         = models.ImageField(upload_to='menu_items/', blank=True)

class CartItem(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity   = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
    ]
    user               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    restaurant         = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    total_price        = models.FloatField()
    delivery_latitude  = models.FloatField()
    delivery_longitude = models.FloatField()
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at         = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item      = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity       = models.IntegerField()
    price_at_time  = models.FloatField()

class Product(models.Model):
    owner       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='items')
    name        = models.CharField(max_length=100)
    price       = models.FloatField()
    description = models.TextField(blank=True)
    available   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
