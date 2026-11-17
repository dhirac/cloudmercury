from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    subject = forms.ChoiceField(label="What do you need?")

    class Meta:
        model = Contact
        fields = ["name", "email", "subject", "message"]
        labels = {"name": "Your name", "message": "Tell us about it"}
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        from cms.models import Service
        titles = list(Service.objects.filter(is_active=True, kind="main").values_list("title", flat=True))
        self.fields["subject"].choices = [(t, t) for t in titles + ["Something else"]]
        self.fields["email"] = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
        self.order_fields(["name", "email", "subject", "message"])
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "input")
