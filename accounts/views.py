from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator

from .models import User, Address
from .forms import UserRegistrationForm, UserUpdateForm, AddressForm


class CustomLoginView(LoginView):
    """Custom login view with modern styling."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name}!')
        return super().form_valid(form)


class UserRegistrationView(CreateView):
    """User registration view."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        username = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, f'Account created successfully! Welcome, {user.first_name}!')
        return response


@method_decorator(login_required, name='dispatch')
class ProfileView(UpdateView):
    """User profile management view."""
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        context['address_form'] = AddressForm()
        return context


@login_required
def add_address(request):
    """Add new address for user."""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('accounts:profile')


@login_required
def delete_address(request, address_id):
    """Delete user address."""
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
    return redirect('accounts:profile')