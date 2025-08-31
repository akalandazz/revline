from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Category, Brand
from .filters import ProductFilter
from .serializers import ProductSerializer
from vehicles.models import Make, VehicleModel, Vehicle


class ProductListView(FilterView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    filterset_class = ProductFilter
    paginate_by = 24
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(part_number__icontains=search_query) |
                Q(oem_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['makes'] = Make.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('images', 'reviews__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:6]
        
        # Reviews
        reviews = product.reviews.all()
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
        context['total_reviews'] = reviews.count()
        
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('brand').prefetch_related('images')
        
        # Pagination
        paginator = Paginator(products, 24)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        
        return context
    


@api_view(['GET'])
def get_models_by_make(request, make_id):
    """Get vehicle models for a specific make"""
    models = VehicleModel.objects.filter(make_id=make_id)
    data = [{'id': model.id, 'name': model.name} for model in models]
    return Response(data)


@api_view(['GET'])
def get_years_by_model(request, model_id):
    """Get available years for a specific model"""
    years = Vehicle.objects.filter(model_id=model_id).values_list(
        'year', flat=True
    ).distinct().order_by('-year')
    return Response(list(years))


@api_view(['POST'])
def search_compatible_parts(request):
    """Search for parts compatible with specific vehicle"""
    make_id = request.data.get('make_id')
    model_id = request.data.get('model_id')
    year = request.data.get('year')
    
    if not all([make_id, model_id, year]):
        return Response({'error': 'Make, model, and year are required'}, status=400)
    
    try:
        vehicle = Vehicle.objects.get(
            make_id=make_id,
            model_id=model_id,
            year=year
        )
        
        # Find compatible products
        compatible_products = Product.objects.filter(
            Q(compatible_vehicles=vehicle) |
            Q(compatible_makes=vehicle.make, compatible_models=vehicle.model) |
            (Q(year_from__lte=year) & Q(year_to__gte=year))
        ).filter(is_active=True).distinct()
        
        serializer = ProductSerializer(compatible_products, many=True)
        return Response(serializer.data)
        
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=404)