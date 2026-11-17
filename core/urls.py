from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path, reverse
from django.utils.http import urlencode
from django.views.static import serve

from accounts.policy import two_factor_on

admin.site.site_header = "CloudMercury admin"
admin.site.site_title = "CloudMercury"


def _admin_login(request, extra_context=None):
    """Send admin sign-ins through our login (Turnstile + two-factor)."""
    return redirect(f"{reverse('accounts:login')}?{urlencode({'next': request.GET.get('next', '/django-admin/')})}")


def _admin_has_permission(request):
    user = request.user
    if not (user.is_active and user.is_staff):
        return False
    if two_factor_on():
        profile = getattr(user, "profile", None)
        return bool(profile and profile.totp_enabled)
    return True


admin.site.login = _admin_login
admin.site.has_permission = _admin_has_permission

def _to_dashboard(request, rest=""):
    """Old /admin/ links and bookmarks go to the CloudMercury dashboard."""
    return redirect("cms:home")


urlpatterns = [
    # /admin/ opens the CloudMercury dashboard. Django's built-in admin is still available
    # at /django-admin/ for advanced tasks (superusers only).
    re_path(r"^admin(?:/(?P<rest>.*))?$", _to_dashboard),
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),       # staff sign-in with Turnstile + two-factor
    path("dashboard/", include("cms.urls")),           # website management dashboard
    # The client portal (hosting, projects, billing) is built but switched off until hosting launches:
    # path("client/", include("dashboard.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("landing.urls")),
]
