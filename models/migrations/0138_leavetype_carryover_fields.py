from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0137_companyconfig_accrual_timezone"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="carry_over_enabled",
            field=models.BooleanField(
                default=False,
                help_text="Whether unused balance is carried over to the immediately following cycle.",
            ),
        ),
        migrations.AddField(
            model_name="leavetype",
            name="carry_over_cap",
            field=models.DecimalField(
                blank=True,
                null=True,
                max_digits=12,
                decimal_places=6,
                help_text="None = no cap. 0 = carry-over enabled but nothing is ever actually carried.",
            ),
        ),
        migrations.AddField(
            model_name="leavetype",
            name="carry_over_expiration_months",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text="Required, strictly positive, whenever carry_over_enabled is True.",
            ),
        ),
    ]
