from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Web views
    path('', views.ProductListView.as_view(), name='product_list'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # API views
    path('api/products/', views.ProductListView.as_view(), name='product_list_api'),
    path('api/makes/<int:make_id>/models/', views.get_models_by_make, name='models_by_make'),
    path('api/models/<int:model_id>/years/', views.get_years_by_model, name='years_by_model'),
    path('api/search-compatible/', views.search_compatible_parts, name='search_compatible'),
]