from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class StyledMixin:
    def _style(self):
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "input")
            field.widget.attrs.setdefault("id", f"id_{name}")


class LoginForm(StyledMixin, forms.Form):
    username = forms.CharField(label="Email or username", max_length=150,
                               widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}))
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
    remember = forms.BooleanField(label="Keep me signed in on this device", required=False)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()
        self.fields["remember"].widget.attrs["class"] = "check"


class SignupForm(StyledMixin, forms.Form):
    first_name = forms.CharField(label="Full name", max_length=150,
                                 widget=forms.TextInput(attrs={"autocomplete": "name"}))
    company = forms.CharField(label="Company (optional)", max_length=160, required=False)
    email = forms.EmailField(label="Work email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(label="Password", strip=False,
                               help_text="At least 10 characters.",
                               widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    terms = forms.BooleanField(label="I agree to the terms of service and privacy policy")

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()
        self.fields["terms"].widget.attrs["class"] = "check"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Sign in instead.")
        return email

    def clean(self):
        data = super().clean()
        pwd = data.get("password")
        if pwd:
            temp = User(username=data.get("email", ""), email=data.get("email", ""),
                        first_name=data.get("first_name", ""))
            try:
                password_validation.validate_password(pwd, temp)
            except forms.ValidationError as e:
                self.add_error("password", e)
        return data

    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(username=d["email"], email=d["email"], password=d["password"],
                                        first_name=d["first_name"])
        user.profile.company = d.get("company", "")
        user.profile.save()
        return user


class CodeForm(StyledMixin, forms.Form):
    code = forms.CharField(label="Authentication code", max_length=12,
                           widget=forms.TextInput(attrs={
                               "autocomplete": "one-time-code", "inputmode": "numeric",
                               "autofocus": True, "placeholder": "123 456", "class": "input input-code",
                           }))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()


class BackupCodeForm(StyledMixin, forms.Form):
    code = forms.CharField(label="Backup code", max_length=12,
                           widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "a1b2-c3d4",
                                                         "class": "input input-code"}))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()


class Disable2FAForm(StyledMixin, forms.Form):
    password = forms.CharField(label="Current password", strip=False, widget=forms.PasswordInput)
    code = forms.CharField(label="Authentication code", max_length=12,
                           widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "inputmode": "numeric"}))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()


class ProfileForm(StyledMixin, forms.Form):
    first_name = forms.CharField(label="Full name", max_length=150)
    email = forms.EmailField(label="Email")
    company = forms.CharField(label="Company", max_length=160, required=False)
    phone = forms.CharField(label="Phone", max_length=40, required=False)

    def __init__(self, *a, user=None, **kw):
        self.user = user
        super().__init__(*a, **kw)
        self._style()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Another account already uses this email.")
        return email


class StyledPasswordChangeForm(StyledMixin, PasswordChangeForm):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()
