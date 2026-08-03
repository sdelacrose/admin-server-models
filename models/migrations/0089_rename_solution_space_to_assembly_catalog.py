from django.db import migrations, models


OLD_SEGMENT = ".product_services.solution_space"
NEW_SEGMENT = ".product_services.assembly_catalog"


def _rewrite_override_keys(overrides, old_segment, new_segment):
    if not isinstance(overrides, dict):
        return {}

    rewritten = {}
    for key, value in overrides.items():
        if not isinstance(key, str):
            continue
        rewritten[key.replace(old_segment, new_segment)] = value
    return rewritten


def rename_solution_space_keys(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    for row in configuration.objects.all().iterator():
        row.overrides = _rewrite_override_keys(row.overrides, OLD_SEGMENT, NEW_SEGMENT)
        row.registry_version = 7
        row.save(update_fields=["overrides", "registry_version"])


def restore_solution_space_keys(apps, schema_editor):
    configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    for row in configuration.objects.all().iterator():
        row.overrides = _rewrite_override_keys(row.overrides, NEW_SEGMENT, OLD_SEGMENT)
        row.registry_version = 6
        row.save(update_fields=["overrides", "registry_version"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0088_display_configuration_registry_version_6"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=7),
        ),
        migrations.RunPython(
            rename_solution_space_keys,
            reverse_code=restore_solution_space_keys,
        ),
    ]
