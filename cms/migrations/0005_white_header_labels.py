from django.db import migrations, models

from cms.models import HEX, IMAGE_TYPES


class Migration(migrations.Migration):
    dependencies = [("cms", "0004_blue_background")]
    operations = [
        migrations.AlterField(
            model_name="sitesettings", name="logo",
            field=models.FileField(blank=True, help_text="Used in the white top bar. SVG or PNG.", upload_to="branding/",
                                   validators=[IMAGE_TYPES], verbose_name="Logo (for light backgrounds)"),
        ),
        migrations.AlterField(
            model_name="sitesettings", name="logo_light",
            field=models.FileField(blank=True, help_text="Used in the footer. SVG or PNG.", upload_to="branding/",
                                   validators=[IMAGE_TYPES], verbose_name="Logo (for dark backgrounds)"),
        ),
        migrations.AlterField(
            model_name="sitesettings", name="dark_color",
            field=models.CharField(default="#004AAD", max_length=7, validators=[HEX],
                                   verbose_name="Background colour (hero, footer)"),
        ),
    ]
