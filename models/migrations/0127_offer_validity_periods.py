from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0126_profile_sub_area_multiselect"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="offer_validity_periods",
            field=ArrayField(
                base_field=models.CharField(max_length=32),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="offer_validity_periods",
            field=ArrayField(
                base_field=models.CharField(max_length=32),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
