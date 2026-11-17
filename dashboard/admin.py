from django.contrib import admin

from .models import Campaign, Invoice, Project, Service, Ticket, TicketMessage


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "plan", "status", "price_monthly", "renews_on")
    list_filter = ("category", "status")
    list_editable = ("status",)
    search_fields = ("name", "domain", "user__email")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "stage", "progress", "due")
    list_filter = ("stage",)
    list_editable = ("stage", "progress")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "channel", "status", "spent", "budget", "leads")
    list_filter = ("channel", "status")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "amount", "status", "issued", "due")
    list_filter = ("status",)
    list_editable = ("status",)


class MessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1
    fields = ("body", "from_staff", "author", "created")
    readonly_fields = ("created",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "user", "category", "priority", "status", "updated")
    list_filter = ("status", "priority", "category")
    list_editable = ("status",)
    inlines = [MessageInline]

    def save_formset(self, request, form, formset, change):
        for obj in formset.save(commit=False):
            if not obj.author_id:
                obj.author = request.user
                obj.from_staff = True
            obj.save()
        formset.save_m2m()
