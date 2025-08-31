from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'part_number', 'category', 'brand', 
        'price', 'stock_quantity', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'brand', 'condition', 'is_active', 
        'is_featured', 'created_at'
    ]
    search_fields = ['name', 'part_number', 'oem_number', 'description']
    prepopulated_fields = {'slug': ('name', 'part_number')}
    filter_horizontal = ['compatible_vehicles', 'compatible_makes', 'compatible_models']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'part_number', 'oem_number', 'category', 'brand')
        }),
        ('Description', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'condition')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions_length', 'dimensions_width', 'dimensions_height')
        }),
        ('Vehicle Compatibility', {
            'fields': ('compatible_vehicles', 'compatible_makes', 'compatible_models', 'year_from', 'year_to'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title']