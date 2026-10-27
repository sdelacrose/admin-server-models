import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0130_companyconfig_correspondence_types"),
    ]

    operations = [
        migrations.CreateModel(
            name="LeaveType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "key",
                    models.SlugField(
                        max_length=100,
                        help_text="Stable identifier (matches LeaveRequest.type going forward).",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(blank=True, null=True)),
                (
                    "deduction_mode",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("calendar_days", "Calendar days"),
                            ("working_days", "Working days"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("cycle_start_date", models.DateField(blank=True, null=True)),
                ("cycle_end_date", models.DateField(blank=True, null=True)),
                ("allow_half_day", models.BooleanField(blank=True, null=True)),
                (
                    "requires_supporting_document",
                    models.BooleanField(blank=True, null=True),
                ),
                ("consumes_balance", models.BooleanField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company_config",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_type_definitions",
                        to="models.companyconfig",
                        help_text="Set for a Company-scope (live, per-solution) leave type.",
                    ),
                ),
                (
                    "global_config",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_type_definitions",
                        to="models.globalconfig",
                        help_text="Set for an Admin-scope (company default template) leave type.",
                    ),
                ),
                (
                    "inherits_from",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="company_overrides",
                        to="models.leavetype",
                        help_text="Admin-scope LeaveType this company-scope entry is based on.",
                    ),
                ),
            ],
            options={
                "ordering": ("global_config_id", "company_config_id", "key"),
            },
        ),
        migrations.AddConstraint(
            model_name="leavetype",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(global_config__isnull=False, company_config__isnull=True)
                    | models.Q(global_config__isnull=True, company_config__isnull=False)
                ),
                name="leave_type_single_scope",
            ),
        ),
        migrations.AddConstraint(
            model_name="leavetype",
            constraint=models.UniqueConstraint(
                condition=models.Q(global_config__isnull=False),
                fields=("global_config", "key"),
                name="unique_admin_leave_type_key",
            ),
        ),
        migrations.AddConstraint(
            model_name="leavetype",
            constraint=models.UniqueConstraint(
                condition=models.Q(company_config__isnull=False),
                fields=("company_config", "key"),
                name="unique_company_leave_type_key",
            ),
        ),
        migrations.CreateModel(
            name="LeaveSubType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.SlugField(max_length=100)),
                ("name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "leave_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sub_types",
                        to="models.leavetype",
                    ),
                ),
            ],
            options={
                "ordering": ("leave_type_id", "key"),
            },
        ),
        migrations.AddConstraint(
            model_name="leavesubtype",
            constraint=models.UniqueConstraint(
                fields=("leave_type", "key"),
                name="unique_leave_subtype_key_per_type",
            ),
        ),
    ]
