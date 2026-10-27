# LOT L04 (SST): single additive field, hand-written like 0135/0137/0138 to
# avoid bundling in the pre-existing, unrelated bank-IBAN drift makemigrations
# also detects (see 0135's own comment).
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0140_staff_contract_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavetype",
            name="is_sst_managed",
            field=models.BooleanField(
                default=False,
                help_text="Managed by the SST module -- excluded from the classic leave request form.",
            ),
        ),
    ]
