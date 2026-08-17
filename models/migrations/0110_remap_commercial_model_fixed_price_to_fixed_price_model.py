from django.db import migrations


OLD_VALUE = "Fixed Price"
NEW_VALUE = "Fixed Price Model"


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


def remap_commercial_model(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "commercial_model" not in field_names:
            continue

        to_update = []
        for obj in model.objects.all().only("id", "commercial_model"):
            current = list(getattr(obj, "commercial_model", []) or [])
            updated = _remap_list(current)
            if updated != current:
                obj.commercial_model = updated
                to_update.append(obj)
        if to_update:
            model.objects.bulk_update(to_update, ["commercial_model"])


def reverse_remap_commercial_model(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "commercial_model" not in field_names:
            continue

        to_update = []
        for obj in model.objects.all().only("id", "commercial_model"):
            current = list(getattr(obj, "commercial_model", []) or [])
            updated = []
            seen = set()
            for item in current:
                value = OLD_VALUE if item == NEW_VALUE else item
                if value in seen:
                    continue
                updated.append(value)
                seen.add(value)
            if updated != current:
                obj.commercial_model = updated
                to_update.append(obj)
        if to_update:
            model.objects.bulk_update(to_update, ["commercial_model"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0109_remap_commercial_model_time_and_material_to_ampersand"),
    ]

    operations = [
        migrations.RunPython(
            remap_commercial_model,
            reverse_code=reverse_remap_commercial_model,
        ),
    ]
