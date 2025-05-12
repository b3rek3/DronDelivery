from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'restaurants', views.RestaurantViewSet)
router.register(r'menu-items', views.MenuItemViewSet, basename='menuitem')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Drone Management
    path('drone/status/<int:order_id>/', views.DroneStatusView.as_view(), name='drone-status'),
    path('drone/fleet/', views.DroneFleetView.as_view(), name='drone-fleet'),
    
    # Delivery Management
    path('delivery/weather/', views.WeatherConditionView.as_view(), name='weather-condition'),
    path('delivery/analytics/', views.DeliveryAnalyticsView.as_view(), name='delivery-analytics'),
] 