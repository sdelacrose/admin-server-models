from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0111_pluralize_time_and_material_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="configuration_visibility",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="configuration_visibility",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
