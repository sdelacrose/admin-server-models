# LOT RH 1 (finishing pass): "working days per country/organization" was referenced by
# the Congés spec but did not exist anywhere in the codebase (calculate_leave_days hardcodes
# Mon-Fri via np.busday_count's default weekmask) -- added here as Admin-scope configuration
# only. Not yet consulted by any balance calculation (explicitly deferred to a later lot).
import django.contrib.postgres.fields
from django.db import migrations, models

from models.models import default_working_days


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0132_backfill_leave_type_rows"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="working_days",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(),
                blank=True,
                default=default_working_days,
                help_text=(
                    "ISO weekday numbers (1=Monday..7=Sunday) treated as working days "
                    "for this organization/country."
                ),
                size=None,
            ),
        ),
    ]
