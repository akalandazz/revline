from django.contrib import admin
from django.conf import settings

# Customize admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'RevLine Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'RevLine Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to RevLine Administration')