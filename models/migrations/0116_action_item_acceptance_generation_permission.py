from django.db import migrations


PERMISSION_KEY = "action_item.generate_acceptance_tests"


def create_permission(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Permission.objects.update_or_create(
        key=PERMISSION_KEY,
        defaults={
            "module": "action_item",
            "name": "Generate acceptance tests with AI",
            "description": (
                "Generate a reviewable FAT/CAT proposal draft from applied project data"
            ),
        },
    )


def remove_permission(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Permission.objects.filter(key=PERMISSION_KEY).delete()


class Migration(migrations.Migration):
    dependencies = [("models", "0115_display_configuration_registry_version_15")]

    operations = [migrations.RunPython(create_permission, remove_permission)]
