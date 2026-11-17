"""Server-side verification for Cloudflare Turnstile."""
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def client_ip(request):
    forwarded = request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def verify_request(request):
    """Return True if the Turnstile token posted with this request is valid."""
    if not getattr(settings, "TURNSTILE_ENABLED", True):
        return True
    token = request.POST.get("cf-turnstile-response", "")
    if not token:
        return False
    data = urllib.parse.urlencode({
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
        "remoteip": client_ip(request),
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(VERIFY_URL, data=data), timeout=8) as resp:
            result = json.loads(resp.read().decode())
    except Exception:  # network error – fail closed
        logger.exception("Turnstile verification failed")
        return False
    return bool(result.get("success"))
