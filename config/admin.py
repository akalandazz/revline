from django.contrib import admin
from django.conf import settings
from django.urls import path
from .admin_views import admin_dashboard

# Customize admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'RevLine Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'RevLine Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to RevLine Administration')

# Override the admin index view by monkey patching
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('', admin_dashboard, name='index'),
    ]
    return custom_urls + urls[1:]  # Skip the original index URL

admin.site.get_urls = get_urls