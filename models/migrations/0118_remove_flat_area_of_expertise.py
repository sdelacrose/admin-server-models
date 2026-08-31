from django.db import migrations


AREA_OF_EXPERTISE_KEY = "area_of_expertise"


def backfill_nested_area_of_expertise(apps, schema_editor):
    from models.hierarchical_configurations import (
        get_default_nested_configuration,
    )

    default_configuration = get_default_nested_configuration(
        AREA_OF_EXPERTISE_KEY
    )
    for model_name in ("GlobalConfig", "ProjectConfigTemplate", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        configs_to_update = []

        for config in model.objects.all().only("id", "nested_configurations"):
            nested = dict(config.nested_configurations or {})
            if AREA_OF_EXPERTISE_KEY in nested:
                continue
            nested[AREA_OF_EXPERTISE_KEY] = default_configuration
            config.nested_configurations = nested
            configs_to_update.append(config)

        if configs_to_update:
            model.objects.bulk_update(configs_to_update, ["nested_configurations"])


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0117_normalize_document_category_codes"),
    ]

    operations = [
        migrations.RunPython(
            backfill_nested_area_of_expertise,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="globalconfig",
            name="area_of_expertise",
        ),
        migrations.RemoveField(
            model_name="projectconfigtemplate",
            name="area_of_expertise",
        ),
        migrations.RemoveField(
            model_name="companyconfig",
            name="area_of_expertise",
        ),
    ]
