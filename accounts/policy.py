"""Site-wide sign-in rules, switched on and off from the dashboard's Security page."""


def two_factor_on():
    """True when two-factor sign-in is switched on for the dashboard."""
    from cms.models import SiteSettings
    return SiteSettings.load().two_factor_required
