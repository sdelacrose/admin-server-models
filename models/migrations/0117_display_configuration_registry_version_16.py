from django.db import migrations, models


def update_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=16)


def restore_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=15)


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0116_action_item_acceptance_generation_permission"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=16),
        ),
        migrations.RunPython(
            update_registry_version,
            reverse_code=restore_registry_version,
        ),
    ]
