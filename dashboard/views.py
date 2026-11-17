from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Profile

from .catalog import CATEGORIES, ORDER_PLANS
from .forms import OrderForm, ReplyForm, TicketForm
from .models import Campaign, Invoice, Project, Service, Ticket, TicketMessage


def portal_required(view):
    """Signed-in users only; staff must have two-factor turned on."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        from accounts.policy import two_factor_on
        if two_factor_on() and request.user.is_staff and not profile.totp_enabled:
            messages.warning(request, "Staff accounts need two-factor authentication. Set it up to continue.")
            return redirect("accounts:setup_2fa")
        request.profile = profile
        return view(request, *args, **kwargs)
    return wrapper


def _greeting():
    h = timezone.localtime().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


@portal_required
def overview(request):
    u = request.user
    services = u.services.exclude(status="cancelled")
    hosting = services.filter(category="web_hosting")
    email = services.filter(category="email_hosting")
    campaigns = u.campaigns.filter(status__in=["live", "paused"])
    projects = u.projects.exclude(stage="launched")
    open_tickets = u.tickets.exclude(status="resolved")
    due = u.invoices.exclude(status="paid")

    month_spend = services.filter(status="active").aggregate(s=Sum("price_monthly"))["s"] or 0
    leads = campaigns.aggregate(s=Sum("leads"))["s"] or 0
    renewals = services.filter(renews_on__isnull=False, renews_on__gte=timezone.localdate()).order_by("renews_on")[:4]

    checklist = [
        {"done": bool(u.first_name and request.profile.company), "label": "Complete your profile",
         "url": "accounts:profile"},
        {"done": request.profile.totp_enabled, "label": "Turn on two-factor authentication",
         "url": "accounts:setup_2fa"},
        {"done": services.exists(), "label": "Order your first service", "url": "dashboard:order"},
    ]

    return render(request, "dashboard/overview.html", {
        "active": "overview", "greeting": _greeting(),
        "services": services, "hosting": hosting, "email": email,
        "campaigns": campaigns[:3], "projects": projects[:3],
        "open_tickets": open_tickets[:4], "open_ticket_count": open_tickets.count(),
        "due_invoices": due, "due_total": due.aggregate(s=Sum("amount"))["s"] or 0,
        "month_spend": month_spend, "leads": leads, "renewals": renewals,
        "checklist": checklist, "checklist_done": all(c["done"] for c in checklist),
    })


@portal_required
def services(request):
    cat = request.GET.get("category", "")
    qs = request.user.services.all()
    if cat:
        qs = qs.filter(category=cat)
    return render(request, "dashboard/services.html", {
        "active": "services", "services": qs, "categories": CATEGORIES, "current": cat,
    })


@portal_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, user=request.user)
    return render(request, "dashboard/service_detail.html", {
        "active": "services", "service": service, "tickets": service.tickets.all()[:5],
    })


@portal_required
def order(request):
    initial = {"category": request.GET.get("category", "web_hosting"), "plan": request.GET.get("plan", ""),
               "domain": request.GET.get("domain", "")}
    form = OrderForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        plan_label = dict(ORDER_PLANS[d["category"]])[d["plan"]]
        service = Service.objects.create(
            user=request.user, category=d["category"], plan=plan_label.split(" – ")[0],
            name=d["domain"] or plan_label.split(" – ")[0], domain=d["domain"], status="pending", notes=d["notes"],
        )
        ticket = Ticket.objects.create(user=request.user, service=service, category="sales",
                                       subject=f"New order: {service.get_category_display()} – {plan_label}")
        TicketMessage.objects.create(ticket=ticket, author=request.user,
                                     body=d["notes"] or "No extra notes.")
        try:
            mail_admins(f"New order from {request.user.email}", f"{plan_label}\nDomain: {d['domain']}\n\n{d['notes']}",
                        fail_silently=True)
        except Exception:
            pass
        messages.success(request, "Order received. We'll confirm the setup within one business day.")
        return redirect("dashboard:services")
    return render(request, "dashboard/order.html", {"active": "services", "form": form, "plans": ORDER_PLANS})


@portal_required
def projects(request):
    return render(request, "dashboard/projects.html", {
        "active": "projects", "projects": request.user.projects.all(), "stages": Project.STAGES,
    })


@portal_required
def campaigns(request):
    qs = request.user.campaigns.all()
    totals = qs.aggregate(spent=Sum("spent"), leads=Sum("leads"), clicks=Sum("clicks"), impressions=Sum("impressions"))
    return render(request, "dashboard/campaigns.html", {"active": "campaigns", "campaigns": qs, "totals": totals})


@portal_required
def billing(request):
    qs = request.user.invoices.all()
    return render(request, "dashboard/billing.html", {
        "active": "billing", "invoices": qs,
        "due_total": qs.exclude(status="paid").aggregate(s=Sum("amount"))["s"] or 0,
        "paid_total": qs.filter(status="paid").aggregate(s=Sum("amount"))["s"] or 0,
    })


@portal_required
def support(request):
    form = TicketForm(request.POST or None, user=request.user,
                      initial={"service": request.GET.get("service")})
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        TicketMessage.objects.create(ticket=ticket, author=request.user, body=form.cleaned_data["message"])
        try:
            mail_admins(f"Ticket #{ticket.pk}: {ticket.subject}", form.cleaned_data["message"], fail_silently=True)
        except Exception:
            pass
        messages.success(request, f"Ticket #{ticket.pk} opened. We reply within 4 business hours.")
        return redirect("dashboard:ticket", pk=ticket.pk)
    return render(request, "dashboard/support.html", {
        "active": "support", "tickets": request.user.tickets.all(), "form": form,
        "show_form": request.method == "POST" or request.GET.get("new"),
    })


@portal_required
def ticket(request, pk):
    t = get_object_or_404(Ticket, pk=pk, user=request.user)
    form = ReplyForm(request.POST or None)
    if request.method == "POST":
        if request.POST.get("action") == "resolve":
            t.status = "resolved"
            t.save()
            messages.success(request, "Ticket marked as resolved.")
            return redirect("dashboard:ticket", pk=t.pk)
        if form.is_valid():
            TicketMessage.objects.create(ticket=t, author=request.user, body=form.cleaned_data["body"])
            t.status = "open"
            t.save()
            messages.success(request, "Reply sent.")
            return redirect("dashboard:ticket", pk=t.pk)
    return render(request, "dashboard/ticket.html", {"active": "support", "ticket": t, "form": form})
