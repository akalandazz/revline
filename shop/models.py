from django.db import models


class SiteSettings(models.Model):
    """Site-wide settings and configuration."""
    
    site_name = models.CharField(max_length=100, default='RevLine')
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Social media links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # SEO settings
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    
    # Business settings
    currency_symbol = models.CharField(max_length=5, default='$')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0875)  # 8.75%
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=75.00)
    
    # Maintenance mode
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Banner(models.Model):
    """Homepage and promotional banners."""
    
    BANNER_TYPES = [
        ('hero', 'Hero Banner'),
        ('promotional', 'Promotional Banner'),
        ('category', 'Category Banner'),
    ]
    
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='banners/')
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='promotional')
    
    # Call to action
    cta_text = models.CharField(max_length=50, blank=True)
    cta_link = models.URLField(blank=True)
    
    # Display settings
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"


class Newsletter(models.Model):
    """Newsletter subscription model."""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """Contact form messages."""
    
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('order', 'Order Related'),
        ('partnership', 'Partnership'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField()
    
    # Admin fields
    is_read = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"