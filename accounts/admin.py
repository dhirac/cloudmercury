from django.contrib import admin

from .models import Profile, SecurityEvent


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "totp_enabled", "totp_enabled_at")
    list_filter = ("totp_enabled",)
    search_fields = ("user__email", "user__username", "company")
    exclude = ("totp_secret", "backup_codes", "totp_last_step")
    readonly_fields = ("totp_enabled_at",)
    actions = ["reset_2fa"]

    @admin.action(description="Reset two-factor (user must set it up again)")
    def reset_2fa(self, request, queryset):
        queryset.update(totp_enabled=False, totp_secret="", backup_codes=[], totp_last_step=None)


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "ip", "created")
    list_filter = ("kind",)
    search_fields = ("user__email", "ip")
