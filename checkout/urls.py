from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # Checkout process
    path('', views.checkout_start, name='checkout'),
    path('contact/', views.checkout_contact, name='contact'),
    path('shipping/', views.checkout_shipping, name='shipping'),
    path('billing/', views.checkout_billing, name='billing'),
    path('shipping-method/', views.checkout_shipping_method, name='shipping_method'),
    path('payment/', views.checkout_payment, name='payment'),
    path('review/', views.checkout_review, name='review'),
    path('success/<str:order_number>/', views.checkout_success, name='success'),
    
    # Order management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
]