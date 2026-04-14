import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Cart, Order, OrderItem


# 🏠 HOME PAGE
def home(request):
    products = Product.objects.all()
    return render(request, "myapp/home.html", {"products": products})


# 🛒 ADD TO CART
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    item.quantity += 1
    item.save()

    return redirect("home")


# 🛒 VIEW CART
def view_cart(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "myapp/cart.html", {
        "items": items,
        "total": total
    })


# ➕ INCREASE
def increase_qty(request, cart_id):
    item = Cart.objects.get(id=cart_id)
    item.quantity += 1
    item.save()
    return JsonResponse({"qty": item.quantity})


# ➖ DECREASE
def decrease_qty(request, cart_id):
    item = Cart.objects.get(id=cart_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return JsonResponse({"qty": item.quantity})


# ❌ REMOVE ITEM (AJAX)
def remove_item(request, cart_id):
    Cart.objects.filter(id=cart_id).delete()
    return JsonResponse({"removed": True})


# 💳 PAYSTACK CHECKOUT
def create_checkout_session(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": request.user.email,
        "amount": int(total * 100),
        "callback_url": "http://127.0.0.1:8000/payment-success/"
    }

    response = requests.post(url, json=data, headers=headers)
    res = response.json()

    return redirect(res["data"]["authorization_url"])


# ✅ SUCCESS PAGE
def paystack_success(request):
    items = Cart.objects.filter(user=request.user)

    total = sum(item.product.price * item.quantity for item in items)

    order = Order.objects.create(
        user=request.user,
        total=total,
        paid=True
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity
        )

    items.delete()

    return render(request, "myapp/success.html")