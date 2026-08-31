from django.db import migrations

from models.configuration_templates import get_project_template_defaults


def backfill_project_config_templates(apps, schema_editor):
    GlobalConfig = apps.get_model("models", "GlobalConfig")
    ProjectConfigTemplate = apps.get_model("models", "ProjectConfigTemplate")

    for global_config in GlobalConfig.objects.iterator():
        owner = {}
        if global_config.company_profile_id:
            owner["company_profile_id"] = global_config.company_profile_id
        elif global_config.user_id:
            owner["user_id"] = global_config.user_id
        else:
            continue

        ProjectConfigTemplate.objects.get_or_create(
            **owner,
            defaults=get_project_template_defaults(global_config),
        )


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0114_project_config_template"),
    ]

    operations = [
        migrations.RunPython(
            backfill_project_config_templates,
            migrations.RunPython.noop,
        ),
    ]
