from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts import totp
from landing.models import Contact

from .models import FAQ, Service, SiteSettings
from .registry import LISTS, SECTIONS

User = get_user_model()


def require_2fa(on=True):
    site = SiteSettings.load()
    site.two_factor_required = on
    site.save()


def staff(two_factor=True):
    u = User.objects.create_user("admin@cloudmercury.test", "admin@cloudmercury.test", "Sup3r-Secret-Pass",
                                 is_staff=True, first_name="Ana")
    if two_factor:
        u.profile.totp_enabled = True
        u.profile.totp_secret = totp.generate_secret()
        u.profile.save()
    return u


class SeedTests(TestCase):
    def test_starting_content_is_loaded(self):
        site = SiteSettings.load()
        self.assertEqual(site.site_name, "CloudMercury")
        self.assertEqual(Service.objects.count(), 6)
        self.assertEqual(FAQ.objects.count(), 5)

    def test_home_shows_seeded_content(self):
        r = self.client.get("/")
        self.assertContains(r, "We build, host and grow your")
        self.assertContains(r, "Software &amp; SaaS development")
        self.assertContains(r, "Launching soon")
        self.assertContains(r, "How much does a project cost?")


class AccessTests(TestCase):
    def test_anonymous_goes_to_login(self):
        r = self.client.get(reverse("cms:home"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r["Location"])

    def test_non_staff_blocked(self):
        u = User.objects.create_user("x@x.test", "x@x.test", "Sup3r-Secret-Pass")
        self.client.force_login(u)
        self.assertEqual(self.client.get(reverse("cms:home")).status_code, 403)

    def test_two_factor_is_off_by_default(self):
        self.assertFalse(SiteSettings.load().two_factor_required)

    def test_staff_without_2fa_allowed_when_switched_off(self):
        self.client.force_login(staff(two_factor=False))
        self.assertEqual(self.client.get(reverse("cms:home")).status_code, 200)

    @override_settings(TURNSTILE_ENABLED=False)
    def test_no_code_asked_when_switched_off(self):
        u = staff()
        r = self.client.post(reverse("accounts:login"), {"username": u.email, "password": "Sup3r-Secret-Pass"})
        self.assertRedirects(r, reverse("cms:home"))

    def test_staff_without_2fa_must_set_it_up(self):
        require_2fa()
        self.client.force_login(staff(two_factor=False))
        self.assertRedirects(self.client.get(reverse("cms:home")), reverse("accounts:setup_2fa"))

    def test_public_signup_is_off(self):
        self.assertEqual(self.client.get("/accounts/signup/").status_code, 404)

    @override_settings(TURNSTILE_ENABLED=False)
    def test_login_with_2fa_lands_on_dashboard(self):
        require_2fa()
        u = staff()
        r = self.client.post(reverse("accounts:login"), {"username": u.email, "password": "Sup3r-Secret-Pass"})
        self.assertRedirects(r, reverse("accounts:verify"))
        code = totp.hotp(u.profile.totp_secret, totp.current_step())
        r = self.client.post(reverse("accounts:verify"), {"code": code})
        self.assertRedirects(r, reverse("cms:home"))


class EditorTests(TestCase):
    def setUp(self):
        self.client.force_login(staff())

    def test_every_page_opens(self):
        for url in [reverse("cms:home"), reverse("cms:inbox"), reverse("accounts:security"),
                    reverse("accounts:profile")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for slug in SECTIONS:
            self.assertEqual(self.client.get(reverse("cms:section", args=[slug])).status_code, 200, slug)
        for slug, data in LISTS.items():
            self.assertEqual(self.client.get(reverse("cms:item_add", args=[slug])).status_code, 200, slug)
            obj = data[0].objects.first()
            self.assertEqual(self.client.get(reverse("cms:item_edit", args=[slug, obj.pk])).status_code, 200, slug)

    def test_edit_hero_updates_site(self):
        site = SiteSettings.load()
        fields = [f for _, fs in SECTIONS["hero"][3] for f in fs]
        data = {f: getattr(site, f) for f in fields}
        data.update(hero_title="Brand new headline", show_hero_visual="on")
        r = self.client.post(reverse("cms:section", args=["hero"]), data)
        self.assertEqual(r.status_code, 302)
        self.assertContains(self.client.get("/"), "Brand new headline")

    def test_bad_colour_rejected(self):
        site = SiteSettings.load()
        fields = [f for _, fs in SECTIONS["branding"][3] for f in fs if f not in ("logo", "logo_light", "favicon")]
        data = {f: getattr(site, f) for f in fields}
        data["primary_color"] = "blue"
        r = self.client.post(reverse("cms:section", args=["branding"]), data)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(SiteSettings.load().primary_color, "#004AAD")

    def test_add_move_hide_delete_faq(self):
        r = self.client.post(reverse("cms:item_add", args=["faqs"]),
                             {"question": "Do you offer hosting?", "answer": "Soon.", "is_active": "on"})
        self.assertEqual(r.status_code, 302)
        new = FAQ.objects.get(question="Do you offer hosting?")
        self.assertEqual(list(FAQ.objects.values_list("pk", flat=True))[-1], new.pk)
        self.client.post(reverse("cms:item_move", args=["faqs", new.pk, "up"]))
        self.assertEqual(list(FAQ.objects.values_list("pk", flat=True))[-2], new.pk)
        self.assertContains(self.client.get("/"), "Do you offer hosting?")
        self.client.post(reverse("cms:item_toggle", args=["faqs", new.pk]))
        self.assertNotContains(self.client.get("/"), "Do you offer hosting?")
        self.client.post(reverse("cms:item_delete", args=["faqs", new.pk]))
        self.assertFalse(FAQ.objects.filter(pk=new.pk).exists())

    def test_hidden_service_leaves_contact_form(self):
        s = Service.objects.get(title="Web hosting")
        self.client.post(reverse("cms:item_toggle", args=["services", s.pk]))
        self.assertNotContains(self.client.get("/"), '<option value="Web hosting"')


class InboxTests(TestCase):
    @mock.patch("landing.views.verify_request", return_value=True)
    def test_message_reaches_inbox(self, _):
        self.client.post("/", {"name": "Rui", "email": "rui@example.com", "subject": "Digital marketing",
                               "message": "Need SEO", "cf-turnstile-response": "x"})
        m = Contact.objects.get()
        self.assertFalse(m.is_read)
        self.client.force_login(staff())
        self.assertContains(self.client.get(reverse("cms:inbox")), "Rui")
        self.client.get(reverse("cms:message", args=[m.pk]))
        m.refresh_from_db()
        self.assertTrue(m.is_read)
        self.client.post(reverse("cms:message", args=[m.pk]), {"action": "delete"})
        self.assertFalse(Contact.objects.exists())


class SwitchTests(TestCase):
    def test_cannot_switch_on_without_own_app(self):
        self.client.force_login(staff(two_factor=False))
        r = self.client.post(reverse("cms:two_factor_switch"), {"state": "on"})
        self.assertRedirects(r, reverse("accounts:setup_2fa"))
        self.assertFalse(SiteSettings.load().two_factor_required)

    def test_switch_on_and_off(self):
        self.client.force_login(staff())
        self.client.post(reverse("cms:two_factor_switch"), {"state": "on"})
        self.assertTrue(SiteSettings.load().two_factor_required)
        self.client.post(reverse("cms:two_factor_switch"), {"state": "off"})
        self.assertFalse(SiteSettings.load().two_factor_required)

    def test_security_page_shows_switch(self):
        self.client.force_login(staff())
        self.assertContains(self.client.get(reverse("accounts:security")), "Two-factor sign-in for the dashboard")


class AdminRedirectTests(TestCase):
    def test_admin_goes_to_dashboard(self):
        for url in ["/admin", "/admin/", "/admin/login/?next=/admin/", "/admin/landing/contact/"]:
            r = self.client.get(url)
            self.assertRedirects(r, reverse("cms:home"), fetch_redirect_response=False, msg_prefix=url)

    @override_settings(TURNSTILE_ENABLED=False)
    def test_login_from_admin_lands_on_dashboard(self):
        u = staff(two_factor=False)
        r = self.client.post(reverse("accounts:login") + "?next=/admin/",
                             {"username": u.email, "password": "Sup3r-Secret-Pass", "next": "/admin/"}, follow=True)
        self.assertEqual(r.redirect_chain[-1][0], reverse("cms:home"))
        self.assertEqual(r.status_code, 200)

    def test_django_admin_still_available_for_superusers(self):
        u = staff(two_factor=False)
        u.is_superuser = True
        u.save()
        self.client.force_login(u)
        self.assertEqual(self.client.get("/django-admin/").status_code, 200)
        self.assertContains(self.client.get(reverse("cms:home")), "Advanced (Django admin)")
