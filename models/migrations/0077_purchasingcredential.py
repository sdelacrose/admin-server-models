# Generated manually for supplier purchasing credentials.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0076_supplierpaymentmethod"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchasingCredential",
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
                    "supplier",
                    models.CharField(
                        choices=[
                            ("festo", "FESTO"),
                            ("wago", "WAGO"),
                            ("ifm", "ifm"),
                            ("hilscher", "Hilscher"),
                            ("phoenix_contact", "Phoenix Contact"),
                            ("schneider_electric", "Schneider Electric"),
                            ("other", "Other"),
                        ],
                        default="festo",
                        max_length=100,
                    ),
                ),
                ("username", models.CharField(max_length=255)),
                ("password", models.CharField(max_length=500)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="purchasing_credentials",
                        to="models.companyprofile",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_purchasing_credentials",
                        to="models.user",
                    ),
                ),
            ],
            options={
                "ordering": ["supplier", "username", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="purchasingcredential",
            index=models.Index(
                fields=["company_profile", "supplier"],
                name="purch_cred_company_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="purchasingcredential",
            index=models.Index(
                fields=["company_profile", "is_active"],
                name="purch_cred_active_idx",
            ),
        ),
    ]
