# Generated manually for supplier purchasing payment methods.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0075_globalconfig_companyconfig_rooms"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupplierPaymentMethod",
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
                ("name", models.CharField(max_length=255)),
                (
                    "method_type",
                    models.CharField(
                        choices=[
                            ("card", "Card"),
                            ("bank_transfer", "Bank transfer"),
                            ("invoice", "Invoice"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=50,
                    ),
                ),
                (
                    "display_details",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                ("reference", models.CharField(blank=True, max_length=255, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company_profile",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="supplier_payment_methods",
                        to="models.companyprofile",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_supplier_payment_methods",
                        to="models.user",
                    ),
                ),
            ],
            options={
                "ordering": ["name", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="supplierpaymentmethod",
            index=models.Index(
                fields=["company_profile", "is_active"],
                name="models_supp_company_149af2_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="supplierpaymentmethod",
            index=models.Index(
                fields=["method_type"],
                name="models_supp_method__f91166_idx",
            ),
        ),
    ]
