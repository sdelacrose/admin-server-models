from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0127_offer_validity_periods"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="document_control_configuration",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="projectconfigtemplate",
            name="document_control_configuration",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="document_control_configuration",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
