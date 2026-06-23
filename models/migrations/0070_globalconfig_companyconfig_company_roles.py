from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0069_globalpublicholiday"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="company_roles",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="company_roles",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
