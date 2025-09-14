from django import forms
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from crispy_forms.bootstrap import FormActions
from accounts.models import Address
from .models import Order, ShippingMethod


class CheckoutContactForm(forms.Form):
    """Form for customer contact information."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(
        validators=[phone_regex],
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Pre-fill form with user data if authenticated
        if user and user.is_authenticated:
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone_number'].initial = user.phone_number

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Contact Information',
                Row(
                    Column('email', css_class='col-md-12'),
                ),
                Row(
                    Column('first_name', css_class='col-md-6'),
                    Column('last_name', css_class='col-md-6'),
                ),
                Row(
                    Column('phone_number', css_class='col-md-12'),
                ),
            )
        )

    def clean_phone_number(self):
        """Clean phone number by removing formatting characters."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove all non-digit characters except +
            phone_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        return phone_number


class ShippingAddressForm(forms.Form):
    """Form for shipping address."""
    
    street_address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123 Main Street'
        })
    )
    apartment = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apt, Suite, Unit (optional)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP/Postal Code'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        initial='United States',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user's default shipping address if available
        if user and user.is_authenticated:
            try:
                address = Address.objects.get(user=user, address_type='shipping', is_default=True)
                self.fields['street_address'].initial = address.street_address
                self.fields['apartment'].initial = address.apartment
                self.fields['city'].initial = address.city
                self.fields['state'].initial = address.state
                self.fields['postal_code'].initial = address.postal_code
                self.fields['country'].initial = address.country
            except Address.DoesNotExist:
                pass
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Shipping Address',
                Row(
                    Column('street_address', css_class='col-md-12'),
                ),
                Row(
                    Column('apartment', css_class='col-md-12'),
                ),
                Row(
                    Column('city', css_class='col-md-6'),
                    Column('state', css_class='col-md-6'),
                ),
                Row(
                    Column('postal_code', css_class='col-md-6'),
                    Column('country', css_class='col-md-6'),
                ),
            )
        )
    
    def clean(self):
        """Custom validation for shipping address form."""
        cleaned_data = super().clean()

        # All required fields are now validated by Django's form validation
        # since they are marked as required=True
        return cleaned_data


class BillingAddressForm(forms.Form):
    """Form for billing address."""
    
    same_as_shipping = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    street_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123 Main Street'
        })
    )
    apartment = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apt, Suite, Unit (optional)'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State/Province'
        })
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ZIP/Postal Code'
        })
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        initial='United States',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user's default billing address if available
        if user and user.is_authenticated:
            try:
                address = Address.objects.get(user=user, address_type='billing', is_default=True)
                self.fields['street_address'].initial = address.street_address
                self.fields['apartment'].initial = address.apartment
                self.fields['city'].initial = address.city
                self.fields['state'].initial = address.state
                self.fields['postal_code'].initial = address.postal_code
                self.fields['country'].initial = address.country
                self.fields['same_as_shipping'].initial = False
            except Address.DoesNotExist:
                pass
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Billing Address',
                Row(
                    Column('same_as_shipping', css_class='col-md-12'),
                ),
                HTML('<div id="billing-address-fields">'),
                Row(
                    Column('street_address', css_class='col-md-12'),
                ),
                Row(
                    Column('apartment', css_class='col-md-12'),
                ),
                Row(
                    Column('city', css_class='col-md-6'),
                    Column('state', css_class='col-md-6'),
                ),
                Row(
                    Column('postal_code', css_class='col-md-6'),
                    Column('country', css_class='col-md-6'),
                ),
                HTML('</div>'),
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        same_as_shipping = cleaned_data.get('same_as_shipping')
        
        if not same_as_shipping:
            # Validate required fields when not same as shipping
            required_fields = ['street_address', 'city', 'state', 'postal_code', 'country']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required.')
        
        return cleaned_data


class ShippingMethodForm(forms.Form):
    """Form for selecting shipping method."""
    
    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None
    )
    
    def __init__(self, *args, **kwargs):
        order_total = kwargs.pop('order_total', 0)
        super().__init__(*args, **kwargs)
        
        # Update queryset to show free shipping where applicable
        self.order_total = order_total
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Shipping Method',
                'shipping_method',
            )
        )


class PaymentForm(forms.Form):
    """Form for payment information."""
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # Credit card fields (only shown when credit card is selected)
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'data-mask': '0000 0000 0000 0000'
        })
    )
    card_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name on Card'
        })
    )
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'data-mask': '00/00'
        })
    )
    card_cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'CVV',
            'data-mask': '000'
        })
    )
    
    # Order notes
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Special instructions or notes for your order (optional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Payment Method',
                'payment_method',
                HTML('<div id="credit-card-fields" style="display: none;">'),
                Row(
                    Column('card_number', css_class='col-md-12'),
                ),
                Row(
                    Column('card_name', css_class='col-md-12'),
                ),
                Row(
                    Column('card_expiry', css_class='col-md-6'),
                    Column('card_cvv', css_class='col-md-6'),
                ),
                HTML('</div>'),
            ),
            Fieldset(
                'Order Notes',
                'notes',
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'credit_card':
            # Validate credit card fields
            required_fields = ['card_number', 'card_name', 'card_expiry', 'card_cvv']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for credit card payments.')
        
        return cleaned_data


class OrderReviewForm(forms.Form):
    """Form for final order review and confirmation."""
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'You must accept the terms and conditions to place your order.'}
    )
    
    newsletter_signup = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('terms_accepted', css_class='col-md-12'),
            ),
            Row(
                Column('newsletter_signup', css_class='col-md-12'),
            ),
            FormActions(
                Submit('submit', 'Place Order', css_class='btn btn-primary btn-lg w-100')
            )
        )