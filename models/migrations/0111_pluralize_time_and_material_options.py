from django.db import migrations


CONTRACT_TYPE_ALIASES = {
    "Time and Material",
    "Time & Material",
    "Time & Materials",
}
CONTRACT_TYPE_VALUE = "Time and Materials"
PREVIOUS_CONTRACT_TYPE_VALUE = "Time and Material"

COMMERCIAL_MODEL_ALIASES = {
    "Time and Material",
    "Time and Materials",
    "Time & Material",
}
COMMERCIAL_MODEL_VALUE = "Time & Materials"
PREVIOUS_COMMERCIAL_MODEL_VALUE = "Time & Material"


def _remap_list(values, aliases, replacement):
    remapped = []
    seen = set()
    for item in values or []:
        value = replacement if item in aliases else item
        if value in seen:
            continue
        remapped.append(value)
        seen.add(value)
    return remapped


def _update_config_values(apps, contract_value, commercial_value):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        update_fields = [
            field_name
            for field_name in ("contract_type", "commercial_model")
            if field_name in field_names
        ]
        if not update_fields:
            continue

        to_update = []
        for obj in model.objects.all().only("id", *update_fields):
            changed = False
            if "contract_type" in update_fields:
                current = list(getattr(obj, "contract_type", []) or [])
                updated = _remap_list(
                    current,
                    CONTRACT_TYPE_ALIASES,
                    contract_value,
                )
                if updated != current:
                    obj.contract_type = updated
                    changed = True

            if "commercial_model" in update_fields:
                current = list(getattr(obj, "commercial_model", []) or [])
                updated = _remap_list(
                    current,
                    COMMERCIAL_MODEL_ALIASES,
                    commercial_value,
                )
                if updated != current:
                    obj.commercial_model = updated
                    changed = True

            if changed:
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, update_fields)


def pluralize_time_and_material_options(apps, schema_editor):
    _update_config_values(
        apps,
        CONTRACT_TYPE_VALUE,
        COMMERCIAL_MODEL_VALUE,
    )


def reverse_pluralize_time_and_material_options(apps, schema_editor):
    _update_config_values(
        apps,
        PREVIOUS_CONTRACT_TYPE_VALUE,
        PREVIOUS_COMMERCIAL_MODEL_VALUE,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0110_remap_commercial_model_fixed_price_to_fixed_price_model"),
    ]

    operations = [
        migrations.RunPython(
            pluralize_time_and_material_options,
            reverse_code=reverse_pluralize_time_and_material_options,
        ),
    ]
