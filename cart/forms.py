from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class AddToCartForm(forms.Form):
    """Form for adding products to cart."""
    
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'min': '1',
            'max': '99',
            'style': 'width: 80px;'
        })
    )
    
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        
        if product:
            self.fields['product_id'].initial = product.id
            
            # Set max quantity based on stock if product manages stock
            if product.manage_stock and product.stock_quantity > 0:
                max_qty = min(99, product.stock_quantity)
                self.fields['quantity'].validators = [MinValueValidator(1), MaxValueValidator(max_qty)]
                self.fields['quantity'].widget.attrs['max'] = str(max_qty)


class CartUpdateForm(forms.Form):
    """Form for updating cart item quantities."""
    
    def __init__(self, *args, **kwargs):
        cart_items = kwargs.pop('cart_items', [])
        super().__init__(*args, **kwargs)
        
        for item in cart_items:
            field_name = f'quantity_{item.product.id}'
            max_qty = 99
            
            if item.product.manage_stock and item.product.stock_quantity > 0:
                max_qty = min(99, item.product.stock_quantity)
            
            self.fields[field_name] = forms.IntegerField(
                min_value=0,
                max_value=max_qty,
                initial=item.quantity,
                validators=[MinValueValidator(0), MaxValueValidator(max_qty)],
                widget=forms.NumberInput(attrs={
                    'class': 'form-control quantity-input',
                    'min': '0',
                    'max': str(max_qty),
                    'data-product-id': item.product.id,
                })
            )