from django.urls import path
from .views import (
    HomeView,
    ProductDetailView,
    CheckoutView,
    add_to_cart,
    remove_from_cart,
    OrderSummaryView,
    remove_single_item_from_cart,
    PaymentView
)

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/detail/<slug>/',
         ProductDetailView.as_view(), name='product_detail'),
    path('order-summary/', OrderSummaryView.as_view(), name='order_summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('remove-item/<slug>/', remove_single_item_from_cart,
         name='remove_single_item_from_cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment')

]
