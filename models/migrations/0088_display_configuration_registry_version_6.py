from django.db import migrations, models


def update_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=6)


def restore_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=5)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0087_add_view_project_purchase_orders_permission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=6),
        ),
        migrations.RunPython(
            update_registry_version,
            reverse_code=restore_registry_version,
        ),
    ]
