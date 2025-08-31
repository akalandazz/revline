from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'billing_address_line_1', 'billing_address_line_2', 'billing_city',
            'billing_state_province', 'billing_postal_code', 'billing_country',
            'shipping_address_line_1', 'shipping_address_line_2', 'shipping_city',
            'shipping_state_province', 'shipping_postal_code', 'shipping_country',
            'customer_notes'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Set required fields
        required_fields = [
            'email', 'first_name', 'last_name',
            'billing_address_line_1', 'billing_city', 'billing_state_province',
            'billing_postal_code', 'billing_country',
            'shipping_address_line_1', 'shipping_city', 'shipping_state_province',
            'shipping_postal_code', 'shipping_country'
        ]
        
        for field_name in required_fields:
            self.fields[field_name].required = True
            
        # Set placeholders
        self.fields['customer_notes'].widget.attrs.update({
            'rows': 3,
            'placeholder': 'Any special instructions or notes...'
        })
    
    def set_address_data(self, prefix, address):
        """Helper method to set address data from Address model"""
        self.fields[f'{prefix}address_line_1'].initial = address.address_line_1
        self.fields[f'{prefix}address_line_2'].initial = address.address_line_2
        self.fields[f'{prefix}city'].initial = address.city
        self.fields[f'{prefix}state_province'].initial = address.state_province
        self.fields[f'{prefix}postal_code'].initial = address.postal_code
        self.fields[f'{prefix}country'].initial = address.country