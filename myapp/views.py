import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from .models import Product, Cart, Order, OrderItem


# ================= HOME =================
def home(request):
    products = Product.objects.all()

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = sum(item.quantity for item in Cart.objects.filter(user=request.user))

    return render(request, "myapp/home.html", {
        "products": products,
        "cart_count": cart_count
    })


# ================= SEARCH =================
def search_products(request):
    query = request.GET.get("q")
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, "myapp/home.html", {
        "products": products,
        "cart_count": 0,
        "query": query
    })


# ================= ADD TO CART =================
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("home")


# ================= CART =================
@login_required
def view_cart(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "myapp/cart.html", {
        "items": items,
        "total": total
    })


# ================= REMOVE ITEM =================
@login_required
def remove_item(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()
    return JsonResponse({"removed": True})


# ================= INCREASE QTY =================
@login_required
def increase_qty(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.quantity += 1
    item.save()
    return JsonResponse({"quantity": item.quantity})


# ================= DECREASE QTY =================
@login_required
def decrease_qty(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return JsonResponse({"deleted": True})


# ================= PAYSTACK CHECKOUT =================
@login_required
def create_checkout_session(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(total * 100),
        "callback_url": "http://127.0.0.1:8000/paystack-success/",
    }

    response = requests.post(url, json=data, headers=headers)
    res = response.json()

    return redirect(res["data"]["authorization_url"])


# ================= PAYMENT SUCCESS =================
@login_required
def paystack_success(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    order = Order.objects.create(
        user=request.user,
        total=total,
        paid=True,
        payment_method="paystack"
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        )

    items.delete()

    return redirect("orders")


# ================= ORDERS =================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "myapp/orders.html", {
        "orders": orders
    })