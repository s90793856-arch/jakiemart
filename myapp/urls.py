from django.urls import path
from . import views

urlpatterns = [
    # HOME
    path('', views.home, name='home'),

    # CART
    path('cart/', views.view_cart, name='cart'),

    # ADD TO CART (IMPORTANT FIX)
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # CART ACTIONS
    path('cart/increase/<int:cart_id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<int:cart_id>/', views.decrease_qty, name='decrease_qty'),
    path('cart/remove/<int:cart_id>/', views.remove_item, name='remove_item'),

    # CHECKOUT + ORDERS
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('payment-success/', views.payment_success, name='success'),
    path('orders/', views.my_orders, name='orders'),
path('search/', views.search_products, name='search'),
]