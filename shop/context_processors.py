from .models import SiteSettings
from .forms import SearchForm
from cart.utils import get_cart_total_items


def site_context(request):
    """Add site-wide context variables."""
    return {
        'site_settings': SiteSettings.get_settings(),
        'search_form': SearchForm(),
    }


def cart_context(request):
    """Add cart context variables."""
    return {
        'cart_total_items': get_cart_total_items(request),
    }