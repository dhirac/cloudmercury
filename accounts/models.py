import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    company = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    totp_secret = models.CharField(max_length=64, blank=True)
    totp_enabled = models.BooleanField(default=False)
    totp_last_step = models.BigIntegerField(null=True, blank=True)
    totp_enabled_at = models.DateTimeField(null=True, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)  # list of hashed codes

    def __str__(self):
        return f"Profile of {self.user}"

    # --- backup codes -------------------------------------------------------
    def generate_backup_codes(self, count=8):
        plain = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(count)]
        self.backup_codes = [make_password(c) for c in plain]
        return plain

    def use_backup_code(self, code):
        code = (code or "").strip().lower()
        for hashed in list(self.backup_codes):
            if check_password(code, hashed):
                self.backup_codes.remove(hashed)
                self.save(update_fields=["backup_codes"])
                return True
        return False

    @property
    def backup_codes_left(self):
        return len(self.backup_codes or [])


class SecurityEvent(models.Model):
    """Simple audit log shown on the security page."""

    KINDS = [
        ("login", "Signed in"),
        ("login_failed", "Failed sign-in"),
        ("2fa_enabled", "Two-factor turned on"),
        ("2fa_disabled", "Two-factor turned off"),
        ("2fa_failed", "Wrong two-factor code"),
        ("backup_used", "Backup code used"),
        ("password", "Password changed"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="security_events")
    kind = models.CharField(max_length=20, choices=KINDS)
    ip = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} – {self.get_kind_display()}"
