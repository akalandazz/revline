from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegistrationForm, ProfileForm, AddressForm
from .models import CustomerProfile, Address


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create customer profile
            CustomerProfile.objects.create(user=user)
            
            # Log user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, 'Account created successfully!')
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=profile)
    
    # Get user's addresses
    addresses = request.user.addresses.all()
    orders = request.user.order_set.all()[:5]  # Recent orders
    
    return render(request, 'users/profile.html', {
        'form': form,
        'addresses': addresses,
        'orders': orders,
    })


@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, remove default from other addresses of same type
            if address.is_default:
                Address.objects.filter(
                    user=request.user,
                    type=address.type,
                    is_default=True
                ).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('users:profile')
    else:
        form = AddressForm()
    
    return render(request, 'users/add_address.html', {'form': form})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            
            # Handle default address logic
            if address.is_default:
                Address.objects.filter(
                    user=request.user,
                    type=address.type,
                    is_default=True
                ).exclude(id=address.id).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('users:profile')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'users/edit_address.html', {
        'form': form,
        'address': address
    })