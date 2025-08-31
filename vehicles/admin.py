from django.contrib import admin
from .models import Make, VehicleModel, Engine, Vehicle


@admin.register(Make)
class MakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make', 'created_at']
    list_filter = ['make', 'created_at']
    search_fields = ['name', 'make__name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Engine)
class EngineAdmin(admin.ModelAdmin):
    list_display = ['name', 'displacement', 'fuel_type']
    list_filter = ['fuel_type']
    search_fields = ['name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'make', 'model', 'year', 'engine']
    list_filter = ['make', 'year', 'engine__fuel_type']
    search_fields = ['make__name', 'model__name']