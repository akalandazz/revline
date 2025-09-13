from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class Order(models.Model):
    """Order model for checkout process."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    # Order identification
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    
    # Customer information
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=17, blank=True)
    
    # Shipping address
    shipping_street_address = models.CharField(max_length=255)
    shipping_apartment = models.CharField(max_length=100, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')
    
    # Billing address
    billing_street_address = models.CharField(max_length=255)
    billing_apartment = models.CharField(max_length=100, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100, default='United States')
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Additional information
    notes = models.TextField(blank=True, help_text="Special instructions or notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        timestamp = timezone.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4().hex)[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"
    
    @property
    def full_name(self):
        """Get customer full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def shipping_address(self):
        """Get formatted shipping address."""
        address_parts = [self.shipping_street_address]
        if self.shipping_apartment:
            address_parts.append(self.shipping_apartment)
        address_parts.extend([
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ])
        return "\n".join(address_parts)
    
    @property
    def billing_address(self):
        """Get formatted billing address."""
        address_parts = [self.billing_street_address]
        if self.billing_apartment:
            address_parts.append(self.billing_apartment)
        address_parts.extend([
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ])
        return "\n".join(address_parts)
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items.all())
    
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'processing']
    
    def mark_as_shipped(self):
        """Mark order as shipped."""
        self.status = 'shipped'
        self.shipped_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Mark order as delivered."""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """Individual items in an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Product snapshot (in case product details change)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['order', 'product']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} (Order #{self.order.order_number})"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.unit_price * self.quantity
        
        # Store product snapshot
        if self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_brand = self.product.brand.name
        
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order status histories'
    
    def __str__(self):
        return f"Order #{self.order.order_number} - {self.get_status_display()}"


class ShippingMethod(models.Model):
    """Available shipping methods."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    estimated_days = models.PositiveIntegerField(help_text="Estimated delivery days")
    is_active = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum order amount for free shipping"
    )
    
    class Meta:
        ordering = ['cost']
    
    def __str__(self):
        return f"{self.name} (${self.cost})"
    
    def is_free_for_order(self, order_total):
        """Check if shipping is free for given order total."""
        return (self.free_shipping_threshold and 
                order_total >= self.free_shipping_threshold)