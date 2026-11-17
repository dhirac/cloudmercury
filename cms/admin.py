from django.contrib import admin

from .models import FAQ, ProcessStep, Service, SiteSettings, Stat, Value, WhyCard

admin.site.register(SiteSettings)
for m in (Service, Stat, Value, ProcessStep, WhyCard, FAQ):
    admin.site.register(m, list_display=("__str__", "order", "is_active"), list_editable=("order", "is_active"))
