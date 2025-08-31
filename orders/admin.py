from django.contrib import admin
from .models import Order, OrderItem, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'payment_status',
        'total_amount', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Customer Details', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Billing Address', {
            'fields': (
                'billing_address_line_1', 'billing_address_line_2',
                'billing_city', 'billing_state_province', 
                'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address_line_1', 'shipping_address_line_2',
                'shipping_city', 'shipping_state_province',
                'shipping_postal_code', 'shipping_country'
            ),
            'classes': ('collapse',)
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('notes', 'customer_notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'base_cost', 'cost_per_kg', 
        'estimated_days_min', 'estimated_days_max', 'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['name']