from django.db import migrations


DOCUMENT_CATEGORY_ALIASES = {
    "General:GEN": "General:GAD",
    "Design:DES": "Design:DTS",
    "Technical:TEC": "Technical:TMP",
}


def _normalize_values(values, aliases):
    normalized = []
    seen = set()
    for item in values or []:
        value = aliases.get(item, item)
        if value in seen:
            continue
        normalized.append(value)
        seen.add(value)
    return normalized


def _normalize_document_categories(apps, aliases):
    for model_name in ("GlobalConfig", "ProjectConfigTemplate", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        configs_to_update = []

        for config in model.objects.all().only("id", "document_categories"):
            current = list(config.document_categories or [])
            normalized = _normalize_values(current, aliases)
            if normalized != current:
                config.document_categories = normalized
                configs_to_update.append(config)

        if configs_to_update:
            model.objects.bulk_update(configs_to_update, ["document_categories"])


def normalize_document_category_codes(apps, schema_editor):
    _normalize_document_categories(apps, DOCUMENT_CATEGORY_ALIASES)


def reverse_document_category_codes(apps, schema_editor):
    reverse_aliases = {
        value: key for key, value in DOCUMENT_CATEGORY_ALIASES.items()
    }
    _normalize_document_categories(apps, reverse_aliases)


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0116_add_project_configuration_action_permissions"),
    ]

    operations = [
        migrations.RunPython(
            normalize_document_category_codes,
            reverse_code=reverse_document_category_codes,
        ),
    ]
