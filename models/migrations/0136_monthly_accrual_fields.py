from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0135_companyconfig_leave_entitlement_activation"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="monthly_accrual_rate",
            field=models.DecimalField(
                blank=True,
                null=True,
                max_digits=8,
                decimal_places=4,
                help_text="Monthly accrual rate for this leave type, or None if not in monthly-accrual mode.",
            ),
        ),
        migrations.AddField(
            model_name="leavetype",
            name="accrual_effective_date",
            field=models.DateField(
                blank=True,
                null=True,
                help_text="No monthly accrual credit is generated for a period before this date.",
            ),
        ),
        migrations.AddField(
            model_name="staff",
            name="contract_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="staff",
            name="contract_end_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
