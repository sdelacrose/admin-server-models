from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0067_replace_sir_with_x_salutation"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="labels",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="labels",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
