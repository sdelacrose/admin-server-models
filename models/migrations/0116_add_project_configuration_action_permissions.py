from django.db import migrations


PERMISSIONS = (
    (
        "ecpmp_configurations.reset",
        "Reset ECPMP Configuration",
        "Can reset ECPMP configurations",
    ),
    (
        "ecpmp_configurations.sync_admin",
        "Sync ECPMP Configuration with Admin",
        "Can sync ECPMP configurations with admin",
    ),
)


def add_project_configuration_permissions(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    for key, name, description in PERMISSIONS:
        Permission.objects.update_or_create(
            key=key,
            defaults={
                "name": name,
                "description": description,
                "module": "ecpmp_configurations",
            },
        )


def remove_project_configuration_permissions(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Permission.objects.filter(
        key__in=[key for key, _name, _description in PERMISSIONS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0115_backfill_project_config_templates"),
    ]

    operations = [
        migrations.RunPython(
            add_project_configuration_permissions,
            remove_project_configuration_permissions,
        ),
    ]
