"""Create a demo client with sample data so the dashboard can be previewed.

    python manage.py seed_demo                 # demo@cloudinovater.com / DemoClient#2026
    python manage.py seed_demo --email you@x.com --password '...'
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Campaign, Invoice, Project, Service, Ticket, TicketMessage


class Command(BaseCommand):
    help = "Create a demo client account with sample services, projects and campaigns."

    def add_arguments(self, parser):
        parser.add_argument("--email", default="demo@cloudinovater.com")
        parser.add_argument("--password", default="DemoClient#2026")

    def handle(self, *args, email, password, **opts):
        User = get_user_model()
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": "Marta Silva"})
        user.set_password(password)
        user.save()
        user.profile.company = "Atlântico Surf Co."
        user.profile.save()

        for m in (Service, Project, Campaign, Invoice, Ticket):
            m.objects.filter(user=user).delete()

        today = timezone.localdate()
        web = Service.objects.create(
            user=user, category="web_hosting", name="atlanticosurf.pt", domain="atlanticosurf.pt", plan="Business",
            status="active", price_monthly=Decimal("12"), renews_on=today + timedelta(days=18),
            disk_used_gb=Decimal("38.4"), disk_total_gb=100, bandwidth_gb=Decimal("214.6"), uptime_30d=Decimal("99.982"))
        Service.objects.create(
            user=user, category="web_hosting", name="shop.atlanticosurf.pt", domain="shop.atlanticosurf.pt",
            plan="Starter", status="active", price_monthly=Decimal("4"), renews_on=today + timedelta(days=46),
            disk_used_gb=Decimal("16.9"), disk_total_gb=20, bandwidth_gb=Decimal("61.2"), uptime_30d=Decimal("100"))
        Service.objects.create(
            user=user, category="email_hosting", name="Team mail", domain="atlanticosurf.pt", plan="Mail Pro",
            status="active", price_monthly=Decimal("21"), renews_on=today + timedelta(days=18),
            mailboxes_used=6, mailboxes_total=8, disk_used_gb=Decimal("72"), disk_total_gb=400)
        Service.objects.create(
            user=user, category="domain", name="atlanticosurf.com", domain="atlanticosurf.com", plan="Register",
            status="provisioning", price_monthly=Decimal("1.25"))

        Project.objects.create(user=user, name="Lesson booking app", summary="Customer app for booking surf lessons and rentals",
                               stage="build", progress=62, next_milestone="Payments with MB WAY and cards",
                               due=today + timedelta(days=34), staging_url="https://staging.atlanticosurf.pt")
        Project.objects.create(user=user, name="Instructor scheduling SaaS", summary="Shift planning for 14 instructors",
                               stage="design", progress=25, next_milestone="Clickable prototype review",
                               due=today + timedelta(days=60))

        Campaign.objects.create(user=user, name="Summer lessons – Lisbon", channel="google", status="live",
                                budget=900, spent=Decimal("612.40"), impressions=48210, clicks=1932, leads=87,
                                weekly_leads="6,9,8,12,14,17,21", starts=today - timedelta(days=45))
        Campaign.objects.create(user=user, name="Local SEO – Costa da Caparica", channel="seo", status="live",
                                budget=450, spent=450, impressions=22900, clicks=1240, leads=41,
                                weekly_leads="3,4,4,6,7,8,9", starts=today - timedelta(days=90))
        Campaign.objects.create(user=user, name="Instagram reels – rentals", channel="meta", status="paused",
                                budget=300, spent=Decimal("188.10"), impressions=31050, clicks=702, leads=19,
                                weekly_leads="2,5,4,3,5", starts=today - timedelta(days=35))

        Invoice.objects.create(user=user, number="CI-2026-0412", description="Hosting, email and domains – November",
                               amount=Decimal("38.25"), status="due", issued=today - timedelta(days=4),
                               due=today + timedelta(days=10))
        Invoice.objects.create(user=user, number="CI-2026-0398", description="Booking app – milestone 2",
                               amount=Decimal("2400"), status="paid", issued=today - timedelta(days=30),
                               due=today - timedelta(days=16))
        Invoice.objects.create(user=user, number="CI-2026-0371", description="Hosting, email and domains – October",
                               amount=Decimal("38.25"), status="paid", issued=today - timedelta(days=34),
                               due=today - timedelta(days=20))

        t = Ticket.objects.create(user=user, service=web, subject="Contact form emails going to spam",
                                  category="support", priority="normal", status="waiting")
        TicketMessage.objects.create(ticket=t, author=user, body="Since last week our contact form emails land in Gmail spam.")
        TicketMessage.objects.create(ticket=t, body="We've added DKIM and DMARC records for atlanticosurf.pt. "
                                                    "Could you send a test message and tell us where it lands?",
                                     from_staff=True)

        self.stdout.write(self.style.SUCCESS(f"Demo client ready: {email} / {password}"))
