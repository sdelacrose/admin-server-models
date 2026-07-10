from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0077_purchasingcredential"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplierpaymentmethod",
            name="card_holder",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="supplierpaymentmethod",
            name="card_last_four",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name="supplierpaymentmethod",
            name="vcn_last_four",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
