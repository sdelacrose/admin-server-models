from copy import deepcopy

from django.db import migrations, models


AREA_OF_EXPERTISE_KEY = "area_of_expertise"


def _known_ids(values, allowed_ids):
    if not isinstance(values, list):
        return []
    return [
        value
        for value in values
        if isinstance(value, str) and value in allowed_ids
    ]


def _clean_area_of_expertise(
    nested_configurations,
    configuration_visibility,
    default_configuration,
):
    nested = (
        deepcopy(nested_configurations)
        if isinstance(nested_configurations, dict)
        else {}
    )
    visibility = (
        deepcopy(configuration_visibility)
        if isinstance(configuration_visibility, dict)
        else {}
    )

    nested[AREA_OF_EXPERTISE_KEY] = deepcopy(default_configuration)

    default_group_ids = {
        group["id"] for group in default_configuration.get("groups", [])
    }
    default_child_ids = {
        child["id"]
        for group in default_configuration.get("groups", [])
        for child in group.get("children", [])
    }
    current_area_visibility = visibility.get(AREA_OF_EXPERTISE_KEY, {})
    if not isinstance(current_area_visibility, dict):
        current_area_visibility = {}

    cleaned_area_visibility = {}
    disabled_group_ids = _known_ids(
        current_area_visibility.get("disabled_group_ids"),
        default_group_ids,
    )
    disabled_child_ids = _known_ids(
        current_area_visibility.get("disabled_child_ids"),
        default_child_ids,
    )
    if disabled_group_ids:
        cleaned_area_visibility["disabled_group_ids"] = disabled_group_ids
    if disabled_child_ids:
        cleaned_area_visibility["disabled_child_ids"] = disabled_child_ids

    if cleaned_area_visibility:
        visibility[AREA_OF_EXPERTISE_KEY] = cleaned_area_visibility
    else:
        visibility.pop(AREA_OF_EXPERTISE_KEY, None)

    return nested, visibility


def remove_custom_area_of_expertise_nodes(apps, schema_editor):
    from models.hierarchical_configurations import (
        get_default_nested_configuration,
    )

    default_configuration = get_default_nested_configuration(
        AREA_OF_EXPERTISE_KEY
    )
    for model_name in ("GlobalConfig", "CompanyConfig"):
        configuration_model = apps.get_model("models", model_name)
        for configuration in configuration_model.objects.iterator():
            nested, visibility = _clean_area_of_expertise(
                configuration.nested_configurations,
                configuration.configuration_visibility,
                default_configuration,
            )
            update_fields = []
            if nested != configuration.nested_configurations:
                configuration.nested_configurations = nested
                update_fields.append("nested_configurations")
            if visibility != configuration.configuration_visibility:
                configuration.configuration_visibility = visibility
                update_fields.append("configuration_visibility")
            if update_fields:
                configuration.save(update_fields=update_fields)


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0124_display_configuration_registry_version_16"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="main_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="sub_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="main_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="sub_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(
            remove_custom_area_of_expertise_nodes,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
