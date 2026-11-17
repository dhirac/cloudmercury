from django import forms

from .catalog import ALL_PLAN_CHOICES, CATEGORIES, ORDER_PLANS
from .models import Ticket


class _Styled:
    def _style(self):
        for name, f in self.fields.items():
            css = "input" if not isinstance(f.widget, forms.Select) else "input select"
            if isinstance(f.widget, forms.Textarea):
                css = "input textarea"
            f.widget.attrs.setdefault("class", css)


class OrderForm(_Styled, forms.Form):
    category = forms.ChoiceField(label="Service", choices=[c for c in CATEGORIES])
    plan = forms.ChoiceField(label="Plan", choices=ALL_PLAN_CHOICES)
    domain = forms.CharField(label="Domain (if you have one)", max_length=253, required=False,
                             widget=forms.TextInput(attrs={"placeholder": "yourbusiness.com"}))
    notes = forms.CharField(label="Anything we should know?", required=False,
                            widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Goals, deadlines, current provider…"}))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()

    def clean(self):
        d = super().clean()
        cat, plan = d.get("category"), d.get("plan")
        if cat and plan and plan not in dict(ORDER_PLANS.get(cat, [])):
            self.add_error("plan", "Pick a plan that belongs to the selected service.")
        return d


class TicketForm(_Styled, forms.ModelForm):
    message = forms.CharField(label="Describe the issue", widget=forms.Textarea(attrs={"rows": 6}))

    class Meta:
        model = Ticket
        fields = ["subject", "category", "priority", "service"]

    def __init__(self, *a, user=None, **kw):
        super().__init__(*a, **kw)
        self.fields["service"].queryset = user.services.exclude(status="cancelled") if user else None
        self.fields["service"].required = False
        self.fields["service"].empty_label = "Not about a specific service"
        self._style()


class ReplyForm(_Styled, forms.Form):
    body = forms.CharField(label="Your reply", widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._style()
