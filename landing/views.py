import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from accounts.turnstile import verify_request
from cms.models import FAQ, ProcessStep, Service, SiteSettings, Stat, Value, WhyCard

from .forms import ContactForm

logger = logging.getLogger(__name__)


def landing(request):
    site = SiteSettings.load()
    form = ContactForm(request.POST or None)
    if request.method == "POST":
        if not verify_request(request):
            form.add_error(None, "Please complete the security check and send again.")
        elif form.is_valid():
            contact = form.save()
            try:
                EmailMessage(
                    subject=f"[Website] {contact.subject}",
                    body=f"{contact.message}\n\n— {contact.name} <{contact.email}>",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[site.notify_email or site.email or settings.CONTACT_INBOX],
                    reply_to=[contact.email],
                ).send(fail_silently=False)
            except Exception:
                logger.exception("Could not email contact message #%s", contact.pk)
            messages.success(request, site.form_success or "Thank you! Your message has been sent.")
            return redirect("/#contact")

    services = Service.objects.filter(is_active=True)
    return render(request, "home.html", {
        "form": form,
        "site": site,
        "services": [s for s in services if s.kind == "main"],
        "extra_services": [s for s in services if s.kind == "extra"],
        "stats": Stat.objects.filter(is_active=True),
        "values": Value.objects.filter(is_active=True),
        "steps": ProcessStep.objects.filter(is_active=True),
        "why_cards": WhyCard.objects.filter(is_active=True),
        "faqs": FAQ.objects.filter(is_active=True),
    })
