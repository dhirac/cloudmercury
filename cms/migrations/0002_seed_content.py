from django.db import migrations


def forwards(apps, schema_editor):
    from cms.defaults import seed
    seed(apps)


class Migration(migrations.Migration):
    dependencies = [("cms", "0001_initial")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
