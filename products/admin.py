from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductReview
)


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


class ProductAttributeValueInline(admin.TabularInline):
    """Inline admin for product attributes."""
    model = ProductAttributeValue
    extra = 1


class ProductReviewInline(admin.TabularInline):
    """Inline admin for product reviews."""
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'review', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ('name', 'parent', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    list_display = ('name', 'is_active', 'product_count', 'website')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('logo',)
        }),
        ('Contact', {
            'fields': ('website',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    list_display = (
        'name', 'sku', 'category', 'brand', 'get_price_display', 
        'stock_quantity', 'is_active', 'is_featured', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'condition', 'category', 'brand', 
        'created_at', 'manage_stock'
    )
    search_fields = ('name', 'sku', 'description', 'compatible_makes', 'compatible_models')
    prepopulated_fields = {'slug': ('name', 'sku')}
    list_editable = ('is_active', 'is_featured', 'stock_quantity')
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'review_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'description', 'short_description')
        }),
        ('Classification', {
            'fields': ('category', 'brand', 'condition')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price', 'cost')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'manage_stock')
        }),
        ('Physical Attributes', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Car Compatibility', {
            'fields': ('compatible_makes', 'compatible_models', 'year_from', 'year_to'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductAttributeValueInline, ProductReviewInline]
    
    def get_price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> <strong>${}</strong>',
                obj.price, obj.sale_price
            )
        return f"${obj.price}"
    get_price_display.short_description = "Price"
    get_price_display.admin_order_field = 'price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model."""
    list_display = ('product', 'image_preview', 'alt_text', 'is_primary', 'order')
    list_filter = ('is_primary', 'product__category')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_primary', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Admin configuration for ProductAttribute model."""
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """Admin configuration for ProductAttributeValue model."""
    list_display = ('product', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('product__name', 'attribute__name', 'value')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview model."""
    list_display = ('product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'review')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('product', 'user', 'rating', 'title', 'review')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_verified_purchase')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')
