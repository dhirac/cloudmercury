from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("login/verify/", views.verify_view, name="verify"),
    # Public sign-up is switched off: create staff users with `python manage.py createsuperuser`.
    path("logout/", views.logout_view, name="logout"),
    path("security/", views.security_view, name="security"),
    path("security/2fa/setup/", views.setup_2fa_view, name="setup_2fa"),
    path("security/2fa/backup-codes/", views.backup_codes_view, name="backup_codes"),
    path("security/2fa/disable/", views.disable_2fa_view, name="disable_2fa"),
    path("profile/", views.profile_view, name="profile"),
]
