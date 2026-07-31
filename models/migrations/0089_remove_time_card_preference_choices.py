from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


PROJECT_TYPE_CHOICES = [
    ("action_item", "Action Item"),
    ("project", "Project"),
    ("documents", "Documents"),
    ("milestone", "Milestone"),
    ("folder", "Folder"),
    ("invoice", "Invoice"),
    ("time_expense", "Expense Card"),
    ("purchase_order", "Purchase Order"),
    ("project_funding", "Project Funding"),
    ("project_phase", "Project Phase"),
    ("object_assessment", "Object Assessment"),
    ("project_team", "Project Team"),
]

COMPANY_TYPE_CHOICES = [
    ("action_item", "Action Item"),
    ("time_expense", "Expense Card"),
    ("invoice", "Invoice"),
    ("folder", "Folder"),
    ("documents", "Documents"),
    ("purchase_order", "Purchase Order"),
    ("leave_request", "Leave Request"),
    ("calendar_event", "Calendar Event"),
    ("monthly_timesheet", "Monthly Timesheet"),
]

REMOVED_TYPE = "time_card"


def scrub_time_card_preferences(apps, schema_editor):
    Preference = apps.get_model("models", "Preference")
    fields = (
        "specific_notify_item_i_own",
        "specific_notify_item_am_part_of",
        "specific_notify_company_item_i_own",
        "specific_notify_company_item_am_part_of",
    )
    for preference in Preference.objects.all().iterator():
        changed = False
        for field_name in fields:
            values = getattr(preference, field_name) or []
            cleaned = [value for value in values if value != REMOVED_TYPE]
            if cleaned != list(values):
                setattr(preference, field_name, cleaned)
                changed = True
        if changed:
            preference.save(update_fields=list(fields))


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0088_remove_dead_preference_project_type_choices"),
    ]

    operations = [
        migrations.RunPython(scrub_time_card_preferences, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="preference",
            name="specific_notify_item_i_own",
            field=ArrayField(
                base_field=models.CharField(
                    choices=PROJECT_TYPE_CHOICES,
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="preference",
            name="specific_notify_item_am_part_of",
            field=ArrayField(
                base_field=models.CharField(
                    choices=PROJECT_TYPE_CHOICES,
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="preference",
            name="specific_notify_company_item_i_own",
            field=ArrayField(
                base_field=models.CharField(
                    choices=COMPANY_TYPE_CHOICES,
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="preference",
            name="specific_notify_company_item_am_part_of",
            field=ArrayField(
                base_field=models.CharField(
                    choices=COMPANY_TYPE_CHOICES,
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
    ]
