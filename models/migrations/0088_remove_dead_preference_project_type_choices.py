from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


PROJECT_TYPE_CHOICES = [
    ("action_item", "Action Item"),
    ("project", "Project"),
    ("documents", "Documents"),
    ("milestone", "Milestone"),
    ("folder", "Folder"),
    ("invoice", "Invoice"),
    ("time_card", "Time Card"),
    ("time_expense", "Expense Card"),
    ("purchase_order", "Purchase Order"),
    ("project_funding", "Project Funding"),
    ("project_phase", "Project Phase"),
    ("object_assessment", "Object Assessment"),
    ("project_team", "Project Team"),
]

REMOVED_PROJECT_TYPES = ("project_external_user", "ecpmp_config")


def scrub_removed_project_types(apps, schema_editor):
    Preference = apps.get_model("models", "Preference")
    for preference in Preference.objects.all().iterator():
        changed = False
        for field_name in (
            "specific_notify_item_i_own",
            "specific_notify_item_am_part_of",
        ):
            values = getattr(preference, field_name) or []
            cleaned = [value for value in values if value not in REMOVED_PROJECT_TYPES]
            if cleaned != list(values):
                setattr(preference, field_name, cleaned)
                changed = True
        if changed:
            preference.save(
                update_fields=[
                    "specific_notify_item_i_own",
                    "specific_notify_item_am_part_of",
                ]
            )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0086_preference_company_notification_fields"),
        ("models", "0087_add_view_project_purchase_orders_permission"),
    ]

    operations = [
        migrations.RunPython(scrub_removed_project_types, migrations.RunPython.noop),
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
    ]
