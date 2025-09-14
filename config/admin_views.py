from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from accounts.models import User
from products.models import Product
from checkout.models import Order
from shop.models import ContactMessage


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard view with statistics and widgets."""
    
    # Get current date and calculate date ranges
    now = timezone.now()
    today = now.date()
    thirty_days_ago = today - timedelta(days=30)
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    
    # Calculate statistics
    stats = calculate_dashboard_stats(today, thirty_days_ago, last_month_start, last_month_end)
    
    # Get recent orders (last 10)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Get low stock products
    low_stock_products = Product.objects.filter(
        manage_stock=True,
        stock_quantity__lte=5,
        is_active=True
    ).order_by('stock_quantity')[:10]
    
    # Get top products (by stock quantity for now, could be by sales)
    top_products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'brand').order_by('-stock_quantity')[:10]
    
    # Generate sales chart data (last 30 days)
    sales_data = generate_sales_chart_data(thirty_days_ago, today)
    
    context = {
        # Statistics
        'total_orders': stats['total_orders'],
        'orders_change': stats['orders_change'],
        'total_revenue': stats['total_revenue'],
        'revenue_change': stats['revenue_change'],
        'total_products': stats['total_products'],
        'low_stock_count': stats['low_stock_count'],
        'total_users': stats['total_users'],
        'users_change': stats['users_change'],
        
        # Widget data
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        
        # Chart data
        'sales_labels': json.dumps(sales_data['labels']),
        'sales_data': json.dumps(sales_data['data']),
    }
    
    return render(request, 'admin/index.html', context)


def calculate_dashboard_stats(today, thirty_days_ago, last_month_start, last_month_end):
    """Calculate dashboard statistics with month-over-month changes."""
    
    # Total orders
    total_orders = Order.objects.count()
    current_month_orders = Order.objects.filter(created_at__date__gte=today.replace(day=1)).count()
    last_month_orders = Order.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end
    ).count()
    orders_change = calculate_percentage_change(current_month_orders, last_month_orders)
    
    # Total revenue
    total_revenue = Order.objects.filter(
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    current_month_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=today.replace(day=1)
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    last_month_revenue = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=last_month_start,
        created_at__date__lte=last_month_end
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    revenue_change = calculate_percentage_change(
        float(current_month_revenue), 
        float(last_month_revenue)
    )
    
    # Total products
    total_products = Product.objects.filter(is_active=True).count()
    
    # Low stock count
    low_stock_count = Product.objects.filter(
        manage_stock=True,
        stock_quantity__lte=5,
        is_active=True
    ).count()
    
    # Total users
    total_users = User.objects.count()
    current_month_users = User.objects.filter(date_joined__date__gte=today.replace(day=1)).count()
    last_month_users = User.objects.filter(
        date_joined__date__gte=last_month_start,
        date_joined__date__lte=last_month_end
    ).count()
    users_change = calculate_percentage_change(current_month_users, last_month_users)
    
    return {
        'total_orders': total_orders,
        'orders_change': orders_change,
        'total_revenue': total_revenue,
        'revenue_change': revenue_change,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_users': total_users,
        'users_change': users_change,
    }


def calculate_percentage_change(current, previous):
    """Calculate percentage change between two values."""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)


def generate_sales_chart_data(start_date, end_date):
    """Generate sales chart data for the specified date range."""
    
    # Create date range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    # Get daily sales data
    daily_sales = {}
    orders = Order.objects.filter(
        payment_status='paid',
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        daily_total=Sum('total_amount')
    )
    
    for order in orders:
        daily_sales[order['created_at__date']] = float(order['daily_total'])
    
    # Prepare chart data
    labels = []
    data = []
    
    for date in date_range:
        labels.append(date.strftime('%m/%d'))
        data.append(daily_sales.get(date, 0))
    
    return {
        'labels': labels,
        'data': data
    }