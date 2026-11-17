from django.conf import settings
from django.db import models

from .catalog import CATEGORIES


class Service(models.Model):
    STATUS = [
        ("pending", "Pending review"),
        ("provisioning", "Setting up"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services")
    category = models.CharField(max_length=20, choices=CATEGORIES)
    name = models.CharField(max_length=160)
    plan = models.CharField(max_length=60, blank=True)
    domain = models.CharField(max_length=253, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    price_monthly = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    renews_on = models.DateField(null=True, blank=True)

    # Usage (fill in what applies)
    disk_used_gb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    disk_total_gb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    mailboxes_used = models.PositiveIntegerField(default=0)
    mailboxes_total = models.PositiveIntegerField(default=0)
    bandwidth_gb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    uptime_30d = models.DecimalField(max_digits=6, decimal_places=3, default=100)

    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "-created"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def disk_pct(self):
        return int(self.disk_used_gb / self.disk_total_gb * 100) if self.disk_total_gb else 0

    @property
    def mailbox_pct(self):
        return int(self.mailboxes_used / self.mailboxes_total * 100) if self.mailboxes_total else 0


class Project(models.Model):
    """Software / SaaS development project."""
    STAGES = [
        ("discovery", "Discovery"),
        ("design", "Design"),
        ("build", "Build"),
        ("testing", "Testing"),
        ("launched", "Launched"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=160)
    summary = models.CharField(max_length=255, blank=True)
    stage = models.CharField(max_length=20, choices=STAGES, default="discovery")
    progress = models.PositiveSmallIntegerField(default=0, help_text="0–100")
    next_milestone = models.CharField(max_length=160, blank=True)
    due = models.DateField(null=True, blank=True)
    staging_url = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    @property
    def stage_index(self):
        return [s for s, _ in self.STAGES].index(self.stage)


class Campaign(models.Model):
    """Digital marketing campaign with headline numbers."""
    CHANNELS = [
        ("seo", "SEO"), ("google", "Google Ads"), ("meta", "Meta Ads"), ("linkedin", "LinkedIn Ads"),
        ("email", "Email"), ("social", "Organic social"), ("content", "Content"),
    ]
    STATUS = [("draft", "Draft"), ("live", "Live"), ("paused", "Paused"), ("ended", "Ended")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=160)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    status = models.CharField(max_length=10, choices=STATUS, default="draft")
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    leads = models.PositiveIntegerField(default=0)
    weekly_leads = models.CharField(max_length=200, blank=True,
                                    help_text="Comma-separated leads per week, oldest first, e.g. 4,6,9,8")
    starts = models.DateField(null=True, blank=True)
    ends = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["status", "-starts"]

    def __str__(self):
        return self.name

    @property
    def ctr(self):
        return round(self.clicks / self.impressions * 100, 2) if self.impressions else 0

    @property
    def cost_per_lead(self):
        return round(self.spent / self.leads, 2) if self.leads else None

    @property
    def spend_pct(self):
        return min(100, int(self.spent / self.budget * 100)) if self.budget else 0

    @property
    def series(self):
        try:
            return [int(x) for x in self.weekly_leads.split(",") if x.strip()]
        except ValueError:
            return []

    @property
    def sparkline_points(self):
        data = self.series
        if len(data) < 2:
            return ""
        hi = max(data) or 1
        w, h = 120, 32
        step = w / (len(data) - 1)
        return " ".join(f"{i * step:.1f},{h - (v / hi) * (h - 4) - 2:.1f}" for i, v in enumerate(data))


class Invoice(models.Model):
    STATUS = [("due", "Due"), ("paid", "Paid"), ("overdue", "Overdue")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invoices")
    number = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default="due")
    issued = models.DateField()
    due = models.DateField()

    class Meta:
        ordering = ["-issued"]

    def __str__(self):
        return self.number


class Ticket(models.Model):
    CATEGORY = [("support", "Technical support"), ("billing", "Billing"), ("sales", "New service / sales"),
                ("project", "Project question")]
    PRIORITY = [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent – site down")]
    STATUS = [("open", "Open"), ("waiting", "Waiting on you"), ("resolved", "Resolved")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY, default="support")
    priority = models.CharField(max_length=10, choices=PRIORITY, default="normal")
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-updated"]

    def __str__(self):
        return f"#{self.pk} {self.subject}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    from_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]
