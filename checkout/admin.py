from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem, OrderStatusHistory, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'product_brand']
    fields = ['product', 'product_name', 'product_sku', 'product_brand', 'quantity', 'unit_price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at', 'created_by']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'full_name', 'email', 'status', 'payment_status', 
        'total_amount', 'created_at', 'order_actions'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 'created_at', 
        'shipping_country', 'billing_country'
    ]
    search_fields = [
        'order_number', 'email', 'first_name', 'last_name', 
        'phone_number', 'shipping_city', 'billing_city'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 'shipped_at', 
        'delivered_at', 'total_items', 'shipping_address_display', 
        'billing_address_display'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_street_address', 'shipping_apartment', 'shipping_city',
                'shipping_state', 'shipping_postal_code', 'shipping_country',
                'shipping_address_display'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_street_address', 'billing_apartment', 'billing_city',
                'billing_state', 'billing_postal_code', 'billing_country',
                'billing_address_display'
            )
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'total_items')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at')
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Customer'
    
    def shipping_address_display(self, obj):
        return format_html('<pre>{}</pre>', obj.shipping_address)
    shipping_address_display.short_description = 'Shipping Address'
    
    def billing_address_display(self, obj):
        return format_html('<pre>{}</pre>', obj.billing_address)
    billing_address_display.short_description = 'Billing Address'
    
    def order_actions(self, obj):
        actions = []
        if obj.can_be_cancelled():
            actions.append('<span style="color: red;">Can Cancel</span>')
        if obj.status == 'processing':
            actions.append('<span style="color: blue;">Ready to Ship</span>')
        return format_html(' | '.join(actions)) if actions else '-'
    order_actions.short_description = 'Actions'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = 'Mark selected orders as processing'
    
    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.mark_as_shipped()
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.mark_as_delivered()
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'processing']).update(status='cancelled')
        self.message_user(request, f'{updated} orders cancelled.')
    mark_as_cancelled.short_description = 'Cancel selected orders'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_sku', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status', 'product_brand', 'created_at']
    search_fields = ['order__order_number', 'product_name', 'product_sku', 'product_brand']
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'product_brand', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'created_by')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'estimated_days', 'free_shipping_threshold', 'is_active']
    list_filter = ['is_active', 'estimated_days']
    search_fields = ['name', 'description']
    list_editable = ['cost', 'estimated_days', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('cost', 'free_shipping_threshold')
        }),
        ('Delivery', {
            'fields': ('estimated_days',)
        }),
    )