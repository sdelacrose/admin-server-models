from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0139_leavetype_quotite_policy"),
    ]

    operations = [
        migrations.AddField(
            model_name="staff",
            name="contract_type",
            field=models.CharField(
                max_length=16,
                null=True,
                blank=True,
                choices=[("permanent", "Permanent"), ("temporary", "Temporary")],
            ),
        ),
    ]
