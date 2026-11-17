import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import totp
from .forms import (BackupCodeForm, CodeForm, Disable2FAForm, LoginForm, ProfileForm, SignupForm,
                    StyledPasswordChangeForm)
from .models import Profile, SecurityEvent
from .policy import two_factor_on
from .turnstile import client_ip, verify_request

User = get_user_model()

PENDING_KEY = "2fa_pending"
PENDING_TTL = 5 * 60          # seconds to enter the 2FA code
MAX_2FA_ATTEMPTS = 5
TURNSTILE_ERROR = "Please complete the security check and try again."


def _log(request, user, kind):
    SecurityEvent.objects.create(
        user=user, kind=kind, ip=client_ip(request)[:64],
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def _safe_next(request, fallback=None):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return nxt
    return reverse(fallback or settings.LOGIN_REDIRECT_URL)


def _complete_login(request, user, remember, next_url):
    login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
    request.session.set_expiry(60 * 60 * 24 * 14 if remember else 0)
    _log(request, user, "login")
    return redirect(next_url)


def _profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


# --- Sign in / sign up / sign out ------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    form = LoginForm(request.POST or None)
    if request.method == "POST":
        if not verify_request(request):
            form.add_error(None, TURNSTILE_ERROR)
        elif form.is_valid():
            user = authenticate(request, username=form.cleaned_data["username"],
                                password=form.cleaned_data["password"])
            if user is None:
                existing = User.objects.filter(email__iexact=form.cleaned_data["username"]).first() or \
                    User.objects.filter(username__iexact=form.cleaned_data["username"]).first()
                if existing:
                    _log(request, existing, "login_failed")
                form.add_error(None, "That email and password don't match. Check them and try again.")
            else:
                next_url = _safe_next(request)
                remember = form.cleaned_data.get("remember", False)
                if two_factor_on() and _profile(user).totp_enabled:
                    request.session[PENDING_KEY] = {
                        "uid": user.pk, "next": next_url, "remember": remember,
                        "ts": time.time(), "attempts": 0,
                    }
                    return redirect("accounts:verify")
                return _complete_login(request, user, remember, next_url)
    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


def verify_view(request):
    pending = request.session.get(PENDING_KEY)
    if not pending or time.time() - pending["ts"] > PENDING_TTL:
        request.session.pop(PENDING_KEY, None)
        messages.info(request, "Your sign-in timed out. Enter your password again.")
        return redirect("accounts:login")

    user = User.objects.filter(pk=pending["uid"]).first()
    if user is None:
        request.session.pop(PENDING_KEY, None)
        return redirect("accounts:login")
    profile = _profile(user)

    use_backup = request.GET.get("method") == "backup" or request.POST.get("method") == "backup"
    form = (BackupCodeForm if use_backup else CodeForm)(request.POST or None)

    if request.method == "POST" and form.is_valid():
        code = form.cleaned_data["code"]
        ok = False
        if use_backup:
            ok = profile.use_backup_code(code)
            if ok:
                _log(request, user, "backup_used")
        else:
            step = totp.verify(profile.totp_secret, code, last_step=profile.totp_last_step)
            if step is not None:
                profile.totp_last_step = step
                profile.save(update_fields=["totp_last_step"])
                ok = True
        if ok:
            request.session.pop(PENDING_KEY, None)
            return _complete_login(request, user, pending["remember"], pending["next"])

        pending["attempts"] += 1
        _log(request, user, "2fa_failed")
        if pending["attempts"] >= MAX_2FA_ATTEMPTS:
            request.session.pop(PENDING_KEY, None)
            messages.error(request, "Too many wrong codes. Sign in again to get a fresh attempt.")
            return redirect("accounts:login")
        request.session[PENDING_KEY] = pending
        form.add_error("code", "That code didn't work. Check your app and enter the newest code."
                       if not use_backup else "That backup code isn't valid or was already used.")

    return render(request, "accounts/verify.html", {
        "form": form, "use_backup": use_backup,
        "attempts_left": MAX_2FA_ATTEMPTS - pending["attempts"],
        "email": user.email,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    form = SignupForm(request.POST or None)
    if request.method == "POST":
        if not verify_request(request):
            form.add_error(None, TURNSTILE_ERROR)
        elif form.is_valid():
            user = form.save()
            login(request, user, backend="accounts.backends.EmailOrUsernameBackend")
            _log(request, user, "login")
            messages.success(request, "Your account is ready. Turn on two-factor authentication to protect it.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "accounts/signup.html", {"form": form, "plan": request.GET.get("plan", ""),
                                                    "domain": request.GET.get("domain", "")})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You've signed out.")
    return redirect("accounts:login")


# --- Security settings ------------------------------------------------------

@login_required
def security_view(request):
    profile = _profile(request.user)
    pwd_form = StyledPasswordChangeForm(request.user, request.POST or None) \
        if request.POST.get("action") == "password" else StyledPasswordChangeForm(request.user)
    if request.method == "POST" and request.POST.get("action") == "password":
        if pwd_form.is_valid():
            pwd_form.save()
            update_session_auth_hash(request, pwd_form.user)
            _log(request, request.user, "password")
            messages.success(request, "Password changed.")
            return redirect("accounts:security")
    return render(request, "dashboard/security.html", {
        "profile": profile,
        "pwd_form": pwd_form,
        "disable_form": Disable2FAForm(),
        "events": request.user.security_events.all()[:12],
        "two_factor_on": two_factor_on(),
        "active": "security",
    })


@login_required
def setup_2fa_view(request):
    profile = _profile(request.user)
    if profile.totp_enabled:
        return redirect("accounts:security")

    secret = request.session.get("2fa_setup_secret")
    if not secret or request.GET.get("new"):
        secret = totp.generate_secret()
        request.session["2fa_setup_secret"] = secret

    form = CodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        step = totp.verify(secret, form.cleaned_data["code"])
        if step is None:
            form.add_error("code", "That code didn't match. Make sure your phone's clock is set automatically, "
                                   "then enter the newest code.")
        else:
            profile.totp_secret = secret
            profile.totp_enabled = True
            profile.totp_last_step = step
            profile.totp_enabled_at = timezone.now()
            codes = profile.generate_backup_codes()
            profile.save()
            request.session.pop("2fa_setup_secret", None)
            request.session["2fa_new_codes"] = codes
            _log(request, request.user, "2fa_enabled")
            return redirect("accounts:backup_codes")

    account = request.user.email or request.user.username
    return render(request, "dashboard/setup_2fa.html", {
        "form": form,
        "secret": totp.format_secret(secret),
        "otpauth": totp.provisioning_uri(secret, account, settings.TOTP_ISSUER),
        "active": "security",
    })


@login_required
def backup_codes_view(request):
    profile = _profile(request.user)
    if not profile.totp_enabled:
        return redirect("accounts:security")
    if request.method == "POST":
        form = CodeForm(request.POST)
        if form.is_valid():
            step = totp.verify(profile.totp_secret, form.cleaned_data["code"], last_step=profile.totp_last_step)
            if step is not None:
                profile.totp_last_step = step
                request.session["2fa_new_codes"] = profile.generate_backup_codes()
                profile.save()
                messages.success(request, "New backup codes created. Your old codes no longer work.")
                return redirect("accounts:backup_codes")
        messages.error(request, "That code didn't work, so your backup codes weren't changed.")
        return redirect("accounts:security")
    codes = request.session.pop("2fa_new_codes", None)
    if not codes:
        return redirect("accounts:security")
    return render(request, "dashboard/backup_codes.html", {"codes": codes, "active": "security"})


@login_required
@require_POST
def disable_2fa_view(request):
    profile = _profile(request.user)
    form = Disable2FAForm(request.POST)
    if form.is_valid() and request.user.check_password(form.cleaned_data["password"]) and \
            totp.verify(profile.totp_secret, form.cleaned_data["code"], last_step=profile.totp_last_step) is not None:
        profile.totp_enabled = False
        profile.totp_secret = ""
        profile.totp_last_step = None
        profile.backup_codes = []
        profile.save()
        _log(request, request.user, "2fa_disabled")
        messages.success(request, "Two-factor authentication is off. We recommend turning it back on.")
    else:
        messages.error(request, "Your password or code was wrong, so two-factor is still on.")
    return redirect("accounts:security")


@login_required
def profile_view(request):
    profile = _profile(request.user)
    initial = {"first_name": request.user.first_name, "email": request.user.email,
               "company": profile.company, "phone": profile.phone}
    form = ProfileForm(request.POST or None, user=request.user, initial=initial)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        u = request.user
        u.first_name, u.email = d["first_name"], d["email"]
        if u.username == initial["email"]:
            u.username = d["email"]
        u.save()
        profile.company, profile.phone = d["company"], d["phone"]
        profile.save()
        messages.success(request, "Profile saved.")
        return redirect("accounts:profile")
    return render(request, "dashboard/profile.html", {"form": form, "active": "profile"})
