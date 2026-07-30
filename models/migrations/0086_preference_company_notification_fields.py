from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0085_display_configuration_registry_version_5"),
        ("models", "0085_update_invoice_status_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="preference",
            name="specific_notify_company_item_am_part_of",
            field=ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("action_item", "Action Item"),
                        ("time_card", "Time Card"),
                        ("time_expense", "Expense Card"),
                        ("invoice", "Invoice"),
                        ("folder", "Folder"),
                        ("documents", "Documents"),
                        ("purchase_order", "Purchase Order"),
                        ("leave_request", "Leave Request"),
                        ("calendar_event", "Calendar Event"),
                        ("monthly_timesheet", "Monthly Timesheet"),
                    ],
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="preference",
            name="specific_notify_company_item_i_own",
            field=ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("action_item", "Action Item"),
                        ("time_card", "Time Card"),
                        ("time_expense", "Expense Card"),
                        ("invoice", "Invoice"),
                        ("folder", "Folder"),
                        ("documents", "Documents"),
                        ("purchase_order", "Purchase Order"),
                        ("leave_request", "Leave Request"),
                        ("calendar_event", "Calendar Event"),
                        ("monthly_timesheet", "Monthly Timesheet"),
                    ],
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
                    choices=[
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
                        ("project_external_user", "Project External User"),
                        ("ecpmp_config", "ECPMP Config"),
                    ],
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
                    choices=[
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
                        ("project_external_user", "Project External User"),
                        ("ecpmp_config", "ECPMP Config"),
                    ],
                    max_length=25,
                ),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
    ]
