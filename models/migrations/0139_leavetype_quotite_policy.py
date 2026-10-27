from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0138_leavetype_carryover_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="prorate_accrual_by_quotite",
            field=models.BooleanField(
                default=False,
                help_text="Whether monthly accrual is prorated by the employee's quotite (StaffQuotiteHistory).",
            ),
        ),
    ]
