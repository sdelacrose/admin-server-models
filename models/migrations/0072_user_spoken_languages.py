from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0071_seed_company_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="spoken_languages",
            field=ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
