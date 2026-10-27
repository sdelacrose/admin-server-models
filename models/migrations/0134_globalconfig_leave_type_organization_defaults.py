# LOT RH 1 (finishing pass, continued): _organization_default previously returned fixed
# Python constants, not anything an Admin could configure -- this field is what it now
# reads live (see models.LeaveType._organization_default), so the "configurable by Admin,
# inherited at read time" requirement is backed by real persisted state, not just code.
from django.db import migrations, models

from models.models import default_leave_type_organization_defaults


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0133_globalconfig_working_days"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="leave_type_organization_defaults",
            field=models.JSONField(
                blank=True,
                default=default_leave_type_organization_defaults,
                help_text=(
                    "Admin-configurable baseline for company-scope leave types that "
                    "have no specific Admin template to inherit from."
                ),
            ),
        ),
    ]
