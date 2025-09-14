from django.contrib import admin
from .models import SiteSettings, Banner, Newsletter, ContactMessage


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for Site Settings."""
    list_display = ('site_name', 'contact_email', 'maintenance_mode', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Business Settings', {
            'fields': ('currency_symbol', 'tax_rate', 'free_shipping_threshold')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Admin configuration for Banner model."""
    list_display = ('title', 'banner_type', 'is_active', 'display_order', 'start_date', 'end_date')
    list_filter = ('banner_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_active', 'display_order')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'description', 'image', 'banner_type')
        }),
        ('Call to Action', {
            'fields': ('cta_text', 'cta_link')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'display_order', 'start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for Newsletter model."""
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    readonly_fields = ('subscribed_at',)
    date_hierarchy = 'subscribed_at'
    
    fieldsets = (
        ('Subscription', {
            'fields': ('email', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin configuration for Contact Message model."""
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('subject', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Details', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Admin', {
            'fields': ('is_read', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Contact messages are created from frontend
        return False
