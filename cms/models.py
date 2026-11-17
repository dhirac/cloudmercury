"""Editable website content for the CloudMercury home page."""
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models

IMAGE_TYPES = FileExtensionValidator(["png", "jpg", "jpeg", "webp", "svg"])
HEX = RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Use a colour code like #004AAD.")

COLORS = [
    ("pink", "Orange"),
    ("amber", "Sky blue"),
    ("blue", "Blue"),
    ("teal", "Green"),
    ("violet", "Brand blue (light)"),
]
ICONS = [
    ("chart", "Chart"), ("code", "Code"), ("server", "Server"), ("mail", "Email"), ("cloud", "Cloud"),
    ("folder", "Folder"), ("shield", "Shield"), ("lock", "Lock"), ("globe", "Globe"), ("users", "People"),
    ("wallet", "Wallet"), ("clock", "Clock"), ("sparkle", "Sparkle"), ("bolt", "Lightning"), ("help", "Help"),
    ("phone", "Phone"), ("pin", "Location"), ("key", "Key"), ("box", "Box"), ("check", "Tick"),
]


class SiteSettings(models.Model):
    """One row holding every single-value setting on the site."""

    # Branding
    site_name = models.CharField(max_length=80, default="CloudMercury")
    logo = models.FileField("Logo (for light backgrounds)", upload_to="branding/", blank=True,
                            validators=[IMAGE_TYPES], help_text="Used in the white top bar. SVG or PNG.")
    logo_light = models.FileField("Logo (for dark backgrounds)", upload_to="branding/", blank=True,
                                  validators=[IMAGE_TYPES], help_text="Used in the footer. SVG or PNG.")
    favicon = models.FileField("Browser tab icon", upload_to="branding/", blank=True, validators=[IMAGE_TYPES])
    primary_color = models.CharField("Brand blue", max_length=7, default="#004AAD", validators=[HEX])
    accent_color = models.CharField("Accent (buttons)", max_length=7, default="#FF6443", validators=[HEX])
    dark_color = models.CharField("Background colour (hero, footer)", max_length=7, default="#004AAD", validators=[HEX])

    # SEO
    seo_title = models.CharField("Page title", max_length=120, blank=True)
    seo_description = models.CharField("Description for Google", max_length=300, blank=True)
    gtm_id = models.CharField("Google Tag Manager ID", max_length=20, blank=True, help_text="For example GTM-57G52HK")

    # Header & hero
    nav_cta = models.CharField("Header button", max_length=40, blank=True)
    hero_title = models.CharField("Headline", max_length=160, blank=True)
    hero_highlight = models.CharField("Highlighted words at the end of the headline", max_length=80, blank=True)
    hero_lead = models.TextField("Intro text", blank=True)
    hero_cta_primary = models.CharField("Main button", max_length=40, blank=True)
    hero_cta_secondary = models.CharField("Second button", max_length=40, blank=True)
    show_hero_visual = models.BooleanField("Show the website picture", default=True)
    hero_card_title = models.CharField("Picture title", max_length=60, blank=True)
    hero_stat1_label = models.CharField(max_length=30, blank=True)
    hero_stat1_value = models.CharField(max_length=20, blank=True)
    hero_stat2_label = models.CharField(max_length=30, blank=True)
    hero_stat2_value = models.CharField(max_length=20, blank=True)
    hero_stat3_label = models.CharField(max_length=30, blank=True)
    hero_stat3_value = models.CharField(max_length=20, blank=True)
    hero_float1_title = models.CharField("Floating card 1 title", max_length=40, blank=True)
    hero_float1_text = models.CharField("Floating card 1 text", max_length=60, blank=True)
    hero_float2_title = models.CharField("Floating card 2 title", max_length=40, blank=True)
    hero_float2_text = models.CharField("Floating card 2 text", max_length=60, blank=True)
    hero_float3_title = models.CharField("Floating card 3 title", max_length=40, blank=True)
    hero_float3_text = models.CharField("Floating card 3 text", max_length=60, blank=True)
    tech_title = models.CharField("Technology strip title", max_length=60, blank=True)
    tech_list = models.TextField("Technologies", blank=True, help_text="One per line.")

    # About
    show_about = models.BooleanField("Show this section", default=True)
    about_kicker = models.CharField("Small label", max_length=40, blank=True)
    about_title = models.CharField("Title", max_length=120, blank=True)
    about_intro = models.TextField("Intro (larger text)", blank=True)
    about_body = models.TextField("Body", blank=True, help_text="Leave an empty line between paragraphs.")
    trust_title = models.CharField("Numbers box title", max_length=120, blank=True)
    trust_text = models.TextField("Numbers box text", blank=True)

    # Services
    services_kicker = models.CharField("Small label", max_length=40, blank=True)
    services_title = models.CharField("Title", max_length=120, blank=True)
    services_lead = models.TextField("Intro", blank=True)

    # Process
    show_process = models.BooleanField("Show this section", default=True)
    process_kicker = models.CharField("Small label", max_length=40, blank=True)
    process_title = models.CharField("Title", max_length=120, blank=True)
    process_lead = models.TextField("Intro", blank=True)

    # Why us
    show_why = models.BooleanField("Show this section", default=True)
    why_kicker = models.CharField("Small label", max_length=40, blank=True)
    why_title = models.CharField("Title", max_length=120, blank=True)
    why_lead = models.TextField("Intro", blank=True)
    industries = models.TextField("Industries", blank=True, help_text="One per line. Leave empty to hide.")

    # FAQ
    show_faq = models.BooleanField("Show this section", default=True)
    faq_kicker = models.CharField("Small label", max_length=40, blank=True)
    faq_title = models.CharField("Title", max_length=120, blank=True)

    # Call to action band
    show_cta = models.BooleanField("Show the call-to-action banner", default=True)
    cta_title = models.CharField("Banner title", max_length=120, blank=True)
    cta_text = models.TextField("Banner text", blank=True)
    cta_button = models.CharField("Banner button", max_length=40, blank=True)

    # Contact
    contact_kicker = models.CharField("Small label", max_length=40, blank=True)
    contact_title = models.CharField("Title", max_length=120, blank=True)
    contact_lead = models.TextField("Intro", blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address1_title = models.CharField("Address 1 title", max_length=60, blank=True)
    address1 = models.CharField("Address 1", max_length=160, blank=True)
    address2_title = models.CharField("Address 2 title", max_length=60, blank=True)
    address2 = models.CharField("Address 2", max_length=160, blank=True)
    form_note = models.CharField("Note under the form", max_length=160, blank=True)
    form_success = models.CharField("Message after sending", max_length=200, blank=True)
    notify_email = models.EmailField("Send new messages to", blank=True,
                                     help_text="Leave empty to use the contact email.")

    # Footer & social
    footer_text = models.TextField("Footer text", blank=True)
    footer_note = models.CharField("Bottom-right note", max_length=60, blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)
    facebook = models.URLField("Facebook", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    x_twitter = models.URLField("X (Twitter)", blank=True)

    # Security
    two_factor_required = models.BooleanField(
        "Two-factor sign-in", default=False,
        help_text="When on, everyone signing in to the dashboard must enter a code from an authenticator app.")

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @staticmethod
    def _lines(text):
        return [l.strip() for l in (text or "").splitlines() if l.strip()]

    @property
    def tech_items(self):
        return self._lines(self.tech_list)

    @property
    def industry_items(self):
        return self._lines(self.industries)

    @property
    def about_paragraphs(self):
        return [p.strip() for p in (self.about_body or "").split("\n\n") if p.strip()]

    @property
    def socials(self):
        return [(n, u) for n, u in [("LinkedIn", self.linkedin), ("Facebook", self.facebook),
                                    ("Instagram", self.instagram), ("X", self.x_twitter)] if u]


class Ordered(models.Model):
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Show on site", default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class Service(Ordered):
    KINDS = [("main", "Large card"), ("extra", "Small card")]
    kind = models.CharField("Card size", max_length=10, choices=KINDS, default="main")
    title = models.CharField(max_length=80)
    text = models.TextField("Description")
    bullets = models.TextField("What's included", blank=True, help_text="One item per line.")
    icon = models.CharField(max_length=20, choices=ICONS, default="chart")
    color = models.CharField(max_length=10, choices=COLORS, default="blue")
    badge = models.CharField("Badge", max_length=30, blank=True, help_text="For example: Launching soon")
    link_text = models.CharField("Link text", max_length=60, blank=True, help_text="Links to the contact form.")

    class Meta(Ordered.Meta):
        verbose_name = "service"

    def __str__(self):
        return self.title

    @property
    def bullet_items(self):
        return [l.strip() for l in self.bullets.splitlines() if l.strip()]


class Stat(Ordered):
    value = models.CharField(max_length=20)
    label = models.CharField(max_length=60)

    class Meta(Ordered.Meta):
        verbose_name = "number"

    def __str__(self):
        return f"{self.value} {self.label}"


class Value(Ordered):
    """Short points in the About section."""
    icon = models.CharField(max_length=20, choices=ICONS, default="sparkle")
    color = models.CharField(max_length=10, choices=COLORS, default="violet")
    title = models.CharField(max_length=80)
    text = models.TextField()

    class Meta(Ordered.Meta):
        verbose_name = "about point"

    def __str__(self):
        return self.title


class ProcessStep(Ordered):
    title = models.CharField(max_length=80)
    text = models.TextField()

    class Meta(Ordered.Meta):
        verbose_name = "process step"

    def __str__(self):
        return self.title


class WhyCard(Ordered):
    icon = models.CharField(max_length=20, choices=ICONS, default="users")
    color = models.CharField(max_length=10, choices=COLORS, default="violet")
    title = models.CharField(max_length=80)
    text = models.TextField()

    class Meta(Ordered.Meta):
        verbose_name = "reason"

    def __str__(self):
        return self.title


class FAQ(Ordered):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    class Meta(Ordered.Meta):
        verbose_name = "question"

    def __str__(self):
        return self.question
