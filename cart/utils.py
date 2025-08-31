from .models import Cart


def get_or_create_cart(request):
    """Get or create cart for user or session."""
    if request.user.is_authenticated:
        # For authenticated users
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Merge session cart if exists
        if request.session.session_key:
            try:
                session_cart = Cart.objects.get(session_key=request.session.session_key)
                if session_cart.items.exists():
                    # Merge session cart items to user cart
                    for session_item in session_cart.items.all():
                        cart.add_item(session_item.product, session_item.quantity)
                    
                    # Delete session cart
                    session_cart.delete()
            except Cart.DoesNotExist:
                pass
        
        return cart
    else:
        # For anonymous users
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def get_cart_total_items(request):
    """Get total items in cart for context processor."""
    try:
        cart = get_or_create_cart(request)
        return cart.total_items
    except:
        return 0