from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0098_add_document_type_codes"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="nested_configurations",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="nested_configurations",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
