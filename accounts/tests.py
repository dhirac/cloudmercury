from unittest import mock

from django.test import TestCase

from landing.models import Contact

from . import totp


class TOTPTests(TestCase):
    def test_rfc6238_vector(self):
        secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        self.assertEqual(totp.hotp(secret, 59 // 30), "287082")

    def test_verify_and_replay(self):
        s = totp.generate_secret()
        step = totp.verify(s, totp.hotp(s, totp.current_step()))
        self.assertIsNotNone(step)
        self.assertIsNone(totp.verify(s, totp.hotp(s, step), last_step=step))


class HomeTests(TestCase):
    data = {"name": "Ana", "email": "ana@example.com", "subject": "Digital marketing", "message": "Hello"}

    def test_home_loads_without_login_links(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Sign in")
        self.assertContains(r, "cf-turnstile")

    def test_contact_requires_turnstile(self):
        r = self.client.post("/", self.data)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "security check")
        self.assertEqual(Contact.objects.count(), 0)

    @mock.patch("landing.views.verify_request", return_value=True)
    def test_contact_saves_message(self, _):
        r = self.client.post("/", {**self.data, "cf-turnstile-response": "x"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Contact.objects.count(), 1)

    def test_client_portal_is_switched_off(self):
        self.assertEqual(self.client.get("/client/").status_code, 404)
