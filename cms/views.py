from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Profile, SecurityEvent
from accounts.policy import two_factor_on
from accounts.turnstile import client_ip
from landing.models import Contact

from .forms import NotesForm, item_form, settings_form
from .models import FAQ, Service, SiteSettings
from .registry import LIST_SECTION, LISTS, SECTIONS


def staff_required(view):
    """Signed-in staff only, with two-factor turned on."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            return render(request, "cms/no_access.html", status=403)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if two_factor_on() and not profile.totp_enabled:
            messages.warning(request, "Turn on two-factor authentication to use the dashboard.")
            return redirect("accounts:setup_2fa")
        return view(request, *args, **kwargs)
    return wrapper


def _ctx(request, **extra):
    extra.setdefault("sections", [(k, v[0], v[1]) for k, v in SECTIONS.items()])
    extra.setdefault("unread", Contact.objects.filter(is_read=False).count())
    return extra


@staff_required
def home(request):
    since = timezone.now() - timedelta(days=30)
    return render(request, "cms/home.html", _ctx(
        request, active="home",
        site=SiteSettings.load(),
        recent=Contact.objects.all()[:6],
        month_messages=Contact.objects.filter(created__gte=since).count(),
        total_messages=Contact.objects.count(),
        services_count=Service.objects.filter(is_active=True).count(),
        faq_count=FAQ.objects.filter(is_active=True).count(),
        profile=request.user.profile,
    ))


@staff_required
def section(request, slug):
    if slug not in SECTIONS:
        raise Http404
    label, icon, description, groups, list_slugs = SECTIONS[slug]
    fields = [f for _, fs in groups for f in fs]
    site = SiteSettings.load()
    Form = settings_form(fields)
    form = Form(request.POST or None, request.FILES or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{label} saved. The website is updated.")
        return redirect("cms:section", slug=slug)
    grouped = [(title, [form[f] for f in fs]) for title, fs in groups]
    lists = []
    for ls in list_slugs:
        Model, singular, plural, _, title_attr, extra = LISTS[ls]
        items = Model.objects.all()
        rows = [(o, getattr(o, title_attr), (o.get_kind_display() if extra == "kind" else getattr(o, extra)) if extra else "")
                for o in items]
        lists.append({"slug": ls, "singular": singular, "plural": plural, "rows": rows})
    return render(request, "cms/section.html", _ctx(
        request, active=slug, slug=slug, label=label, description=description, form=form,
        grouped=grouped, lists=lists, site=site,
        has_files=any(f in ("logo", "logo_light", "favicon") for f in fields),
    ))


def _list(slug):
    if slug not in LISTS:
        raise Http404
    return LISTS[slug]


@staff_required
def item_edit(request, slug, pk=None):
    Model, singular, plural, fields, title_attr, _ = _list(slug)
    obj = get_object_or_404(Model, pk=pk) if pk else None
    Form = item_form(Model, fields)
    form = Form(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        if obj is None:
            last = Model.objects.order_by("-order").first()
            item.order = (last.order + 1) if last else 0
        item.save()
        messages.success(request, f"{singular.capitalize()} saved.")
        return redirect("cms:section", slug=LIST_SECTION[slug])
    return render(request, "cms/item_form.html", _ctx(
        request, active=LIST_SECTION[slug], form=form, obj=obj, singular=singular, plural=plural,
        section_slug=LIST_SECTION[slug], section_label=SECTIONS[LIST_SECTION[slug]][0],
    ))


@staff_required
@require_POST
def item_delete(request, slug, pk):
    Model, singular, *_ = _list(slug)
    get_object_or_404(Model, pk=pk).delete()
    messages.success(request, f"{singular.capitalize()} deleted.")
    return redirect("cms:section", slug=LIST_SECTION[slug])


@staff_required
@require_POST
def item_move(request, slug, pk, direction):
    Model = _list(slug)[0]
    with transaction.atomic():
        items = list(Model.objects.all())
        for i, o in enumerate(items):          # normalise order values
            o.order = i
        idx = next(i for i, o in enumerate(items) if o.pk == pk)
        swap = idx - 1 if direction == "up" else idx + 1
        if 0 <= swap < len(items):
            items[idx].order, items[swap].order = items[swap].order, items[idx].order
        for o in items:
            Model.objects.filter(pk=o.pk).update(order=o.order)
    return redirect(reverse("cms:section", kwargs={"slug": LIST_SECTION[slug]}) + f"#list-{slug}")


@staff_required
@require_POST
def item_toggle(request, slug, pk):
    Model, singular, *_ = _list(slug)
    o = get_object_or_404(Model, pk=pk)
    o.is_active = not o.is_active
    o.save(update_fields=["is_active"])
    messages.success(request, f"{singular.capitalize()} {'shown on' if o.is_active else 'hidden from'} the website.")
    return redirect("cms:section", slug=LIST_SECTION[slug])


# --- Messages ---------------------------------------------------------------

@staff_required
def inbox(request):
    qs = Contact.objects.all()
    show = request.GET.get("show", "all")
    q = request.GET.get("q", "").strip()
    if show == "unread":
        qs = qs.filter(is_read=False)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(subject__icontains=q) | Q(message__icontains=q))
    page = Paginator(qs, 25).get_page(request.GET.get("page"))
    return render(request, "cms/inbox.html", _ctx(request, active="inbox", page=page, show=show, q=q))


@staff_required
def message_detail(request, pk):
    m = get_object_or_404(Contact, pk=pk)
    if not m.is_read:
        m.is_read = True
        m.save(update_fields=["is_read"])
    form = NotesForm(request.POST or None, instance=m)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            m.delete()
            messages.success(request, "Message deleted.")
            return redirect("cms:inbox")
        if action == "unread":
            m.is_read = False
            m.save(update_fields=["is_read"])
            messages.success(request, "Marked as unread.")
            return redirect("cms:inbox")
        if form.is_valid():
            form.save()
            messages.success(request, "Notes saved.")
            return redirect("cms:message", pk=m.pk)
    return render(request, "cms/message.html", _ctx(request, active="inbox", m=m, form=form))


@staff_required
@require_POST
def inbox_mark_all(request):
    n = Contact.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, f"{n} message{'s' if n != 1 else ''} marked as read.")
    return redirect("cms:inbox")


@staff_required
@require_POST
def two_factor_switch(request):
    """Turn site-wide two-factor sign-in on or off."""
    site = SiteSettings.load()
    turn_on = request.POST.get("state") == "on"
    if turn_on and not request.user.profile.totp_enabled:
        messages.warning(request, "Set up two-factor on your own account first, so you don't lock yourself out. "
                                  "Then switch it on for everyone.")
        return redirect("accounts:setup_2fa")
    site.two_factor_required = turn_on
    site.save(update_fields=["two_factor_required", "updated"])
    SecurityEvent.objects.create(user=request.user, kind="2fa_enabled" if turn_on else "2fa_disabled",
                                 ip=client_ip(request)[:64], user_agent=request.META.get("HTTP_USER_AGENT", "")[:255])
    if turn_on:
        messages.success(request, "Two-factor sign-in is on. Everyone must enter a code from their app to sign in.")
    else:
        messages.success(request, "Two-factor sign-in is off. Sign-in only needs a password and the security check.")
    return redirect("accounts:security")
