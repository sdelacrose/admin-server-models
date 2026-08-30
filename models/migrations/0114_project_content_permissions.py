from django.db import migrations, models


PERMISSIONS = {
    "project_content": {
        "view": "View generated project documents and templates",
        "create": "Create generated project document records",
        "update": "Review generated project document drafts",
        "generate": "Generate project documents with AI",
        "approve": "Approve generated project document revisions",
        "manage": "Manage company project document templates",
        "full_access": "Full access to generated project documents",
    },
    "acceptance_tests": {
        "view": "View project acceptance tests",
        "create": "Create project acceptance criteria",
        "update": "Update project acceptance criteria",
        "delete": "Delete project acceptance criteria",
        "generate": "Generate acceptance criteria with AI",
        "full_access": "Full access to project acceptance tests",
    },
}


def create_permissions(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    for module, actions in PERMISSIONS.items():
        for action, name in actions.items():
            Permission.objects.update_or_create(
                key=f"{module}.{action}",
                defaults={
                    "module": module,
                    "name": name,
                    "description": name,
                },
            )


def remove_permissions(apps, schema_editor):
    Permission = apps.get_model("models", "Permission")
    Permission.objects.filter(
        key__in=[
            f"{module}.{action}"
            for module, actions in PERMISSIONS.items()
            for action in actions
        ]
    ).delete()


def update_registry_version(apps, schema_editor):
    Configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    Configuration.objects.update(registry_version=14)


def restore_registry_version(apps, schema_editor):
    Configuration = apps.get_model("models", "SolutionDisplayConfiguration")
    Configuration.objects.update(registry_version=13)


class Migration(migrations.Migration):
    dependencies = [("models", "0113_display_configuration_registry_version_12")]

    operations = [
        migrations.RunPython(create_permissions, remove_permissions),
        migrations.AlterField(
            model_name="solutiondisplayconfiguration",
            name="registry_version",
            field=models.PositiveIntegerField(default=14),
        ),
        migrations.RunPython(update_registry_version, restore_registry_version),
    ]
