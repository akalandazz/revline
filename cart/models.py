from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Cart(models.Model):
    """Shopping cart model."""
    
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Calculate total cart price."""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def is_empty(self):
        """Check if cart is empty."""
        return not self.items.exists()
    
    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()
    
    def add_item(self, product, quantity=1):
        """Add or update item in cart."""
        cart_item, created = self.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_item(self, product):
        """Remove item from cart."""
        try:
            cart_item = self.items.get(product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_item_quantity(self, product, quantity):
        """Update item quantity in cart."""
        try:
            cart_item = self.items.get(product=product)
            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()
            return True
        except CartItem.DoesNotExist:
            return False


class CartItem(models.Model):
    """Individual items in shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def unit_price(self):
        """Get unit price of the product."""
        return self.product.get_price
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        # Update cart timestamp when item is modified
        super().save(*args, **kwargs)
        self.cart.save()


class WishlistItem(models.Model):
    """User wishlist items."""
    
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"