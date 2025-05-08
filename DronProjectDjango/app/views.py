from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Restaurant, MenuItem, Order, OrderItem
from .forms import LoginForm, RegistrationForm
from django.urls import reverse

def home(request):
    products = Product.objects.filter(available=True)
    return render(request, 'home.html', {'products': products})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('home')
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Account created, you can now log in.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# … здесь вы будете добавлять остальные view-функции: market, cart, checkout, restaurant_menu и т.д. …
