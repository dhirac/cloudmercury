from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("cms", "0002_seed_content")]
    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="two_factor_required",
            field=models.BooleanField(
                default=False,
                help_text="When on, everyone signing in to the dashboard must enter a code from an authenticator app.",
                verbose_name="Two-factor sign-in",
            ),
        ),
    ]
