from django.db import migrations, models

from cms.models import HEX


def to_blue(apps, schema_editor):
    S = apps.get_model("cms", "SiteSettings")
    S.objects.filter(dark_color__iexact="#0A1936").update(dark_color="#004AAD")


def to_navy(apps, schema_editor):
    S = apps.get_model("cms", "SiteSettings")
    S.objects.filter(dark_color__iexact="#004AAD").update(dark_color="#0A1936")


class Migration(migrations.Migration):
    dependencies = [("cms", "0003_sitesettings_two_factor_required")]
    operations = [
        migrations.AlterField(
            model_name="sitesettings", name="dark_color",
            field=models.CharField(default="#004AAD", max_length=7, verbose_name="Background colour (header, hero, footer)",
                                   validators=[HEX]),
        ),
        migrations.RunPython(to_blue, to_navy),
    ]
