from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address


class AddressInline(admin.TabularInline):
    """Inline admin for user addresses."""
    model = Address
    extra = 0
    fields = ('address_type', 'is_default', 'street_address', 'apartment', 'city', 'state', 'postal_code', 'country')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    list_editable = ('is_verified', 'is_active')
    readonly_fields = ('date_joined', 'last_login', 'created_at', 'updated_at')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    inlines = [AddressInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for Address model."""
    list_display = ('user', 'address_type', 'is_default', 'city', 'state', 'country', 'created_at')
    list_filter = ('address_type', 'is_default', 'country', 'state')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'street_address', 'city')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'address_type', 'is_default')
        }),
        ('Address Details', {
            'fields': ('street_address', 'apartment', 'city', 'state', 'postal_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
