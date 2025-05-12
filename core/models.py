# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    budget = models.FloatField(default=1000.0)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='core_user_groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_permissions',
        related_query_name='user',
    )

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo_path   = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price       = models.FloatField()
    image_path  = models.ImageField(upload_to='menu_item_images/', blank=True, null=True)
    restaurant  = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    menu_item  = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity   = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'menu_item'],
                name='unique_cart_per_user_per_item'
            )
        ]

    def __str__(self):
        return f"{self.quantity} × {self.menu_item.name}"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        CREATED    = 'CREATED',    'Created'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        COMPLETED  = 'COMPLETED',  'Completed'
        CANCELLED  = 'CANCELLED',  'Cancelled'

    user               = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    restaurant         = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total_price        = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_latitude  = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    status             = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED
    )
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order         = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    menu_item     = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity      = models.PositiveIntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.menu_item.name} (Order #{self.order.id})"
