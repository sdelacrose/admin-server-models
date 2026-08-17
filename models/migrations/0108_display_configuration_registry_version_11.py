from django.db import migrations, models


def update_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=11)


def restore_registry_version(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    configuration.objects.update(registry_version=10)


class Migration(migrations.Migration):

    dependencies = [
        (
            "models",
            "0107_split_contract_standard_into_international_and_major_project_model",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=11),
        ),
        migrations.RunPython(
            update_registry_version,
            reverse_code=restore_registry_version,
        ),
    ]
