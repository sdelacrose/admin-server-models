from django.db import migrations

NEW_EXPENSE_TYPES = [
    "milage",
    "car",
    "hotel",
    "transport",
    "parking",
    "gasoline",
    "food",
    "taxi",
    "phone",
    "hardware",
    "software",
    "other",
]

LEGACY_DEFAULT_EXPENSE_TYPES = {
    "milage",
    "parking",
    "train fare",
    "printing",
    "other",
}

RENAME_EXPENSE_TYPES = {
    "train fare": "transport",
}


def _normalize_expense_types(current):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    renamed = [RENAME_EXPENSE_TYPES.get(item, item) for item in values]

    customs = []
    for item in renamed:
        if item in LEGACY_DEFAULT_EXPENSE_TYPES:
            continue
        if item not in NEW_EXPENSE_TYPES:
            customs.append(item)

    ordered = list(NEW_EXPENSE_TYPES)
    seen = set(ordered)
    for custom in customs:
        if custom not in seen:
            ordered.append(custom)
            seen.add(custom)
    return ordered


def replace_expense_types(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "expense_types" not in field_names:
            continue

        to_update = []
        for obj in model.objects.all().only("id", "expense_types"):
            current = list(getattr(obj, "expense_types", []) or [])
            updated = _normalize_expense_types(current)
            if updated != current:
                obj.expense_types = updated
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, ["expense_types"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0095_replace_company_document_types"),
    ]

    operations = [
        migrations.RunPython(
            replace_expense_types,
            migrations.RunPython.noop,
        ),
    ]
