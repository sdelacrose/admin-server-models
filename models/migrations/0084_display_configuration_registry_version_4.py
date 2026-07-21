from django.db import migrations, models


def update_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=4)


def restore_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=3)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0083_display_configuration_registry_version_3"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.RunPython(
            update_registry_version,
            reverse_code=restore_registry_version,
        ),
    ]
