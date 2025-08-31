from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML

from .models import User, Address


class UserRegistrationForm(UserCreationForm):
    """User registration form with enhanced fields."""
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'class': 'form-control'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (Optional)',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'phone_number', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            'email',
            'username',
            'phone_number',
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100 mt-3')
        )
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password',
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'form-control'
        })


class UserUpdateForm(forms.ModelForm):
    """User profile update form."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            'email',
            'phone_number',
            'date_of_birth',
            Submit('submit', 'Update Profile', css_class='btn btn-primary mt-3')
        )


class AddressForm(forms.ModelForm):
    """Address form for billing and shipping."""
    
    class Meta:
        model = Address
        fields = ('address_type', 'street_address', 'apartment', 'city', 'state', 'postal_code', 'country', 'is_default')
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, etc. (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'United States'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'address_type',
            'street_address',
            'apartment',
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('state', css_class='form-group col-md-3 mb-3'),
                Column('postal_code', css_class='form-group col-md-3 mb-3'),
            ),
            'country',
            'is_default',
            Submit('submit', 'Add Address', css_class='btn btn-primary')
        )