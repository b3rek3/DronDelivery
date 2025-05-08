from django.urls import path
from . import views

urlpatterns = [
    path('',        views.home,        name='home'),
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    # TODO: добавить остальные маршруты: market, cart, add_to_cart, checkout…
]
