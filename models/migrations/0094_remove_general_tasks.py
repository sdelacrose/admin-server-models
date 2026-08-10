from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0093_replace_industrial_project_types"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="globalconfig",
            name="general_tasks",
        ),
        migrations.RemoveField(
            model_name="companyconfig",
            name="general_tasks",
        ),
    ]
