from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('restaurants/', views.RestaurantsView.as_view(), name='restaurants'),
    path('restaurant/<int:restaurant_id>/', views.RestaurantMenuView.as_view(), name='restaurant_menu'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add_to_cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update_cart/<int:cart_item_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order_confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('orders/', views.OrdersView.as_view(), name='orders'),
    path('create_order/', views.CreateOrderView.as_view(), name='create_order'),
    path('start_drone/', views.StartDroneView.as_view(), name='start_drone'),
    path('complete_delivery/', views.CompleteDeliveryView.as_view(), name='complete_delivery'),
]