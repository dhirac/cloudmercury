from django.conf import settings


def site(request):
    return {
        "TURNSTILE_SITE_KEY": settings.TURNSTILE_SITE_KEY,
        "TURNSTILE_ENABLED": settings.TURNSTILE_ENABLED,
        "SITE_NAME": "CloudInovater",
    }
