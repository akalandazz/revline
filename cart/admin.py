from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, WishlistItem


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ('total_price', 'unit_price', 'created_at', 'updated_at')
    fields = ('product', 'quantity', 'unit_price', 'total_price', 'created_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model."""
    list_display = ('cart_identifier', 'user_email', 'total_items', 'total_price', 'is_empty', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'session_key')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'total_price', 'is_empty')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'session_key')
        }),
        ('Statistics', {
            'fields': ('total_items', 'total_price', 'is_empty'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CartItemInline]
    
    def cart_identifier(self, obj):
        if obj.user:
            return f"User: {obj.user.email}"
        return f"Session: {obj.session_key[:8]}..."
    cart_identifier.short_description = 'Cart Owner'
    
    def user_email(self, obj):
        return obj.user.email if obj.user else 'Anonymous'
    user_email.short_description = 'User Email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items__product')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for Cart Item model."""
    list_display = ('cart_owner', 'product', 'quantity', 'unit_price', 'total_price', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'product__category', 'product__brand')
    search_fields = ('cart__user__email', 'product__name', 'product__sku')
    readonly_fields = ('total_price', 'unit_price', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Cart Item', {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'total_price'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cart_owner(self, obj):
        if obj.cart.user:
            return obj.cart.user.email
        return f"Session: {obj.cart.session_key[:8]}..."
    cart_owner.short_description = 'Cart Owner'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cart__user', 'product')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin configuration for Wishlist Item model."""
    list_display = ('user', 'product', 'product_price', 'product_availability', 'created_at')
    list_filter = ('created_at', 'product__category', 'product__brand', 'product__is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'product__name', 'product__sku')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Wishlist Item', {
            'fields': ('user', 'product')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def product_price(self, obj):
        return f"${obj.product.get_price}"
    product_price.short_description = 'Price'
    
    def product_availability(self, obj):
        if obj.product.is_in_stock:
            return format_html('<span style="color: green;">In Stock</span>')
        return format_html('<span style="color: red;">Out of Stock</span>')
    product_availability.short_description = 'Availability'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')
