from django import forms

from landing.models import Contact

from .models import SiteSettings

MAX_UPLOAD = 2 * 1024 * 1024


def style(form):
    for name, f in form.fields.items():
        w = f.widget
        if isinstance(w, forms.CheckboxInput):
            w.attrs.setdefault("class", "check")
        elif isinstance(w, forms.ClearableFileInput):
            w.attrs.setdefault("class", "file")
        elif isinstance(w, forms.Select):
            w.attrs.setdefault("class", "input select")
        elif isinstance(w, forms.Textarea):
            w.attrs.setdefault("class", "input textarea")
            w.attrs.setdefault("rows", 3)
        else:
            w.attrs.setdefault("class", "input")


def settings_form(fields):
    """Build a ModelForm for the given SiteSettings fields."""
    widgets = {}
    for f in fields:
        if f.endswith("_color"):
            widgets[f] = forms.TextInput(attrs={"type": "color", "class": "input color"})
        elif f in ("about_body", "hero_lead", "tech_list", "industries", "about_intro"):
            widgets[f] = forms.Textarea(attrs={"rows": 5})

    class Meta:
        model = SiteSettings
        fields_ = fields

    Meta.fields = fields
    Meta.widgets = widgets

    def __init__(self, *a, **kw):
        forms.ModelForm.__init__(self, *a, **kw)
        style(self)

    def clean(self):
        data = forms.ModelForm.clean(self)
        for name in ("logo", "logo_light", "favicon"):
            f = data.get(name)
            if f and hasattr(f, "size") and f.size > MAX_UPLOAD:
                self.add_error(name, "This file is larger than 2 MB. Upload a smaller file.")
        return data

    return type("SettingsForm", (forms.ModelForm,), {"Meta": Meta, "__init__": __init__, "clean": clean})


def item_form(model, fields):
    class Meta:
        pass
    Meta.model = model
    Meta.fields = fields
    Meta.widgets = {"text": forms.Textarea(attrs={"rows": 4}), "answer": forms.Textarea(attrs={"rows": 5}),
                    "bullets": forms.Textarea(attrs={"rows": 6})}

    def __init__(self, *a, **kw):
        forms.ModelForm.__init__(self, *a, **kw)
        style(self)

    return type(f"{model.__name__}Form", (forms.ModelForm,), {"Meta": Meta, "__init__": __init__})


class NotesForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Only visible to your team"})}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        style(self)
