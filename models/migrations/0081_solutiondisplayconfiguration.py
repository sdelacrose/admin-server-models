import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0080_globalconfig_companyconfig_skills"),
    ]

    operations = [
        migrations.CreateModel(
            name="SolutionDisplayConfiguration",
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
                    "solution",
                    models.CharField(
                        choices=[
                            (
                                "energy_consultant_solution",
                                "Energy Consultant Solution",
                            ),
                            ("enterprise_solution", "Enterprise Solution"),
                            ("core_solution", "Core Solution"),
                        ],
                        max_length=64,
                    ),
                ),
                (
                    "registry_version",
                    models.PositiveIntegerField(default=1),
                ),
                ("overrides", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solution_display_configurations",
                        to="models.companyprofile",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_solution_display_configurations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["company_id", "solution"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("company", "solution"),
                        name="unique_company_solution_display_config",
                    )
                ],
            },
        ),
    ]
