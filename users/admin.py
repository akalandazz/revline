from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import CustomerProfile, Address

User = get_user_model()


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profiles'
    filter_horizontal = ['vehicles']


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [CustomerProfileInline, AddressInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'type', 'first_name', 'last_name',
        'city', 'state_province', 'is_default'
    ]
    list_filter = ['type', 'is_default', 'country']
    search_fields = ['user__username', 'first_name', 'last_name', 'city']