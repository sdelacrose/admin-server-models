# Generated manually to centralize reusable skills in scope configuration.

import django.contrib.postgres.fields
from django.db import migrations, models

from models.models import default_skills


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0079_limit_hr_manager_booking_mutations"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="skills",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=default_skills,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="skills",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=default_skills,
                size=None,
            ),
        ),
    ]
