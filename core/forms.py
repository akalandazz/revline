from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Newsletter, ContactMessage


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""
    
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': True,
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'newsletter-form'
        self.helper.layout = Layout(
            Row(
                Column('email', css_class='col-md-8'),
                Column(
                    Submit('submit', 'Subscribe', css_class='btn btn-primary w-100'),
                    css_class='col-md-4'
                ),
                css_class='g-2'
            )
        )


class ContactForm(forms.ModelForm):
    """Contact form for customer inquiries."""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
            }),
            'subject': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Please describe your inquiry in detail...',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            'subject',
            'message',
            Submit('submit', 'Send Message', css_class='btn btn-primary btn-lg mt-3')
        )


class SearchForm(forms.Form):
    """Global search form."""
    
    q = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for car parts, brands, categories...',
            'autocomplete': 'off',
        }),
        label='',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_action = '/search/'
        self.helper.layout = Layout(
            Row(
                Column('q', css_class='col-10'),
                Column(
                    Submit('submit', 'Search', css_class='btn btn-primary w-100'),
                    css_class='col-2'
                ),
                css_class='g-0'
            )
        )