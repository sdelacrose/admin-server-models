from django.db import migrations


OLD_VALUE = "Time & Materials"
NEW_VALUE = "Time and Material"
CONFIG_FIELDS = (
    "contract_type",
    "commercial_model",
)


def _remap_list(values):
    remapped = []
    seen = set()
    for item in values or []:
        value = NEW_VALUE if item == OLD_VALUE else item
        if value in seen:
            continue
        remapped.append(value)
        seen.add(value)
    return remapped


def remap_time_and_material(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        update_fields = [field for field in CONFIG_FIELDS if field in field_names]
        if not update_fields:
            continue

        to_update = []
        for obj in model.objects.all().only("id", *update_fields):
            changed = False
            for field in update_fields:
                current = list(getattr(obj, field, []) or [])
                updated = _remap_list(current)
                if updated != current:
                    setattr(obj, field, updated)
                    changed = True
            if changed:
                to_update.append(obj)
        if to_update:
            model.objects.bulk_update(to_update, update_fields)


def reverse_remap_time_and_material(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        update_fields = [field for field in CONFIG_FIELDS if field in field_names]
        if not update_fields:
            continue

        to_update = []
        for obj in model.objects.all().only("id", *update_fields):
            changed = False
            for field in update_fields:
                current = list(getattr(obj, field, []) or [])
                updated = []
                seen = set()
                for item in current:
                    value = OLD_VALUE if item == NEW_VALUE else item
                    if value in seen:
                        continue
                    updated.append(value)
                    seen.add(value)
                if updated != current:
                    setattr(obj, field, updated)
                    changed = True
            if changed:
                to_update.append(obj)
        if to_update:
            model.objects.bulk_update(to_update, update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0103_display_configuration_registry_version_10"),
    ]

    operations = [
        migrations.RunPython(
            remap_time_and_material,
            reverse_code=reverse_remap_time_and_material,
        ),
    ]
