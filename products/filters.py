import django_filters
from django import forms
from .models import Product, Category, Brand
from vehicles.models import Make, VehicleModel


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search products...'})
    )
    part_number = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Part number...'})
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label="All Categories"
    )
    brand = django_filters.ModelChoiceFilter(
        queryset=Brand.objects.all(),
        empty_label="All Brands"
    )
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={'placeholder': 'Min price'})
    )
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        widget=forms.NumberInput(attrs={'placeholder': 'Max price'})
    )
    make = django_filters.ModelChoiceFilter(
        field_name='compatible_makes',
        queryset=Make.objects.all(),
        empty_label="All Makes"
    )
    model = django_filters.ModelChoiceFilter(
        field_name='compatible_models',
        queryset=VehicleModel.objects.all(),
        empty_label="All Models"
    )
    year_from = django_filters.NumberFilter(
        field_name='year_from',
        lookup_expr='lte',
        widget=forms.NumberInput(attrs={'placeholder': 'From year'})
    )
    year_to = django_filters.NumberFilter(
        field_name='year_to',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={'placeholder': 'To year'})
    )
    in_stock = django_filters.BooleanFilter(
        field_name='stock_quantity',
        lookup_expr='gt',
        widget=forms.CheckboxInput()
    )
    
    class Meta:
        model = Product
        fields = []