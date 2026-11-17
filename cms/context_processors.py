from .registry import SECTIONS


def _unread():
    from landing.models import Contact
    return Contact.objects.filter(is_read=False).count()


def _two_factor():
    from accounts.policy import two_factor_on
    return two_factor_on()


def nav(request):
    """Menu items for the management dashboard sidebar."""
    return {
        "cms_sections": [(k, v[0], v[1]) for k, v in SECTIONS.items()],
        "cms_unread": _unread,   # evaluated only when a template uses it
        "cms_two_factor_on": _two_factor,
    }
