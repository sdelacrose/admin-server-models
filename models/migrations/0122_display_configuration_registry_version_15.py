from django.db import migrations, models


def update_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=15)


def restore_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=14)


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0121_add_customer_demand_company_document_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.RunPython(
            update_registry_version,
            reverse_code=restore_registry_version,
        ),
    ]
