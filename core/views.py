from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, View, FormView, TemplateView
from django.contrib.auth.forms import UserCreationForm  # Django's built-in form
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import logout
from .models import User, Restaurant, MenuItem, CartItem, Order, OrderItem
from .forms import CartItemForm, UpdateCartItemForm, OrderForm, CustomUserCreationForm


class HomeView(TemplateView):
    template_name = 'core/home.html'


class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    next_page = 'core:home'  # Default redirect after successful login

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful!')
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse(self.next_page)


class RegistrationView(FormView):
    template_name = 'core/register.html'
    form_class = CustomUserCreationForm
    success_url = '/login/'

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Your account has been created! You can now log in')
        return super().form_valid(form)


class RestaurantsView(ListView):
    model = Restaurant
    template_name = 'core/restaurants.html'
    context_object_name = 'restaurants'


class RestaurantMenuView(ListView):
    model = MenuItem
    template_name = 'core/restaurant_menu.html'
    context_object_name = 'menu_items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = get_object_or_404(Restaurant, id=self.kwargs['restaurant_id'])
        context['form'] = CartItemForm()
        return context

    def get_queryset(self):
        self.restaurant = get_object_or_404(Restaurant, id=self.kwargs['restaurant_id'])
        return MenuItem.objects.filter(restaurant=self.restaurant)


class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'core/cart.html'
    context_object_name = 'cart_items'
    login_url = 'core:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        
        # Calculate total
        total = sum(item.menu_item.price * item.quantity for item in cart_items)
        context['total'] = total
        context['update_form'] = UpdateCartItemForm()
        return context

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class AddToCartView(LoginRequiredMixin, View):
    login_url = 'core:login'

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        form = CartItemForm(request.POST)
        if form.is_valid():
            menu_item = get_object_or_404(MenuItem, id=form.cleaned_data['menu_item_id'])
            existing_item = CartItem.objects.filter(
                user=request.user,
                menu_item=menu_item
            ).first()

            if existing_item:
                existing_item.quantity += form.cleaned_data['quantity']
                existing_item.save()
            else:
                cart_item = CartItem(
                    user=request.user,
                    menu_item=menu_item,
                    quantity=form.cleaned_data['quantity']
                )
                cart_item.save()

            messages.success(request, 'Item added to cart!')
        return redirect('core:cart')


class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, cart_item_id):
        form = UpdateCartItemForm(request.POST)
        if form.is_valid():
            cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
            cart_item.quantity = form.cleaned_data['quantity']
            cart_item.save()
            messages.success(request, 'Cart updated!')
        return redirect('core:cart')
    login_url = 'core:login'


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart!')
        return redirect('core:cart')
    login_url = 'core:login'


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'core/checkout.html'
    form_class = OrderForm
    success_url = '/order_confirmation/'
    login_url = 'core:login'

    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, 'Your cart is empty!')
            return redirect('core:cart')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = CartItem.objects.filter(user=self.request.user)
        
        # Calculate subtotal for each item and total
        total = 0
        for item in cart_items:
            item.subtotal = item.menu_item.price * item.quantity
            total += item.subtotal
            
        context['cart_items'] = cart_items
        context['total'] = total
        return context

    def form_valid(self, form):
        cart_items = CartItem.objects.filter(user=self.request.user)
        if not cart_items:
            messages.warning(self.request, 'Your cart is empty!')
            return redirect('core:cart')

        # Create order
        restaurant = cart_items[0].menu_item.restaurant
        total = sum(item.menu_item.price * item.quantity for item in cart_items)

        order = Order(
            user=self.request.user,
            restaurant=restaurant,
            total_price=total,
            delivery_latitude=form.cleaned_data['delivery_latitude'],
            delivery_longitude=form.cleaned_data['delivery_longitude']
        )
        order.save()

        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menu_item=cart_item.menu_item,
                quantity=cart_item.quantity,
                price_at_time=cart_item.menu_item.price
            )
            order_item.save()

        # Clear cart
        CartItem.objects.filter(user=self.request.user).delete()

        messages.success(self.request, 'Order placed successfully!')
        return redirect(reverse('core:order_confirmation', kwargs={'order_id': order.id}))


class OrderConfirmationView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/order_confirmation.html'
    context_object_name = 'order'
    login_url = 'core:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, id=self.kwargs['order_id'])


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/orders.html'
    context_object_name = 'orders'
    login_url = 'core:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('core:home')

    def post(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out!')
        return redirect('core:home')


class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            lat = float(request.POST.get('lat'))
            lon = float(request.POST.get('lon'))
            
            # Get cart items
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items:
                return JsonResponse({'error': 'Your cart is empty!'}, status=400)
            
            # Create order
            restaurant = cart_items[0].menu_item.restaurant
            total = sum(item.menu_item.price * item.quantity for item in cart_items)
            
            order = Order(
                user=request.user,
                restaurant=restaurant,
                total_price=total,
                delivery_latitude=lat,
                delivery_longitude=lon,
                status=Order.OrderStatus.CREATED
            )
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order=order,
                    menu_item=cart_item.menu_item,
                    quantity=cart_item.quantity,
                    price_at_time=cart_item.menu_item.price
                )
                order_item.save()
            
            # Clear cart
            cart_items.delete()
            
            return JsonResponse({'order_id': order.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    login_url = 'core:login'


class StartDroneView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            if order.status != Order.OrderStatus.CREATED:
                return JsonResponse({'error': 'Invalid order status'}, status=400)
            
            order.status = Order.OrderStatus.IN_TRANSIT
            order.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    login_url = 'core:login'


class CompleteDeliveryView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            if order.status != Order.OrderStatus.IN_TRANSIT:
                return JsonResponse({'error': 'Invalid order status'}, status=400)
            
            order.status = Order.OrderStatus.COMPLETED
            order.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    login_url = 'core:login'
