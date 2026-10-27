from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0136_monthly_accrual_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="companyconfig",
            name="accrual_timezone",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
