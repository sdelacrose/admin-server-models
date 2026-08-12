from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


NEW_CONTRACT_TYPES = [
    "Fixed Price",
    "Time & Materials",
    "EPC/EPCM",
    "Subcontract",
    "Framework Agreement",
    "Professional Services",
    "Technical Assistance (TA)",
    "Turnkey",
    "Call-Off Contract",
    "Other",
]
NEW_CONTRACT_STANDARDS = [
    "FIDIC Red Book",
    "FIDIC Yellow Book",
    "FIDIC Silver Book",
    "FIDIC White Book",
    "NEC3",
    "NEC4",
    "BOOT",
    "BOT",
    "PPP",
    "PFI",
]
NEW_COMMERCIAL_MODELS = [
    "Fixed Price",
    "Time & Materials",
    "Cost Reimbursable",
    "Target Cost",
    "Pain / Gain Share",
]
NEW_SUPPORTING_AGREEMENTS = [
    "NDA (Non-Disclosure Agreement)",
    "Framework Agreement",
    "Consortium Agreement",
    "Joint Venture Agreement",
    "Contract Amendment (Addendum)",
]
LEGACY_CONTRACT_TYPE_MAP = {
    "Time and Material": "Time & Materials",
}
LEGACY_DEFAULT_CONTRACT_TYPES = {
    "Fixed Price",
    "Time and Material",
    "Time & Materials",
    "Other",
}


def _normalize_contract_types(current):
    values = []
    for item in current or []:
        value = str(item).strip()
        if not value:
            continue
        values.append(LEGACY_CONTRACT_TYPE_MAP.get(value, value))

    customs = [item for item in values if item not in LEGACY_DEFAULT_CONTRACT_TYPES]
    ordered = list(NEW_CONTRACT_TYPES)
    seen = set(ordered)
    for custom in customs:
        if custom not in seen:
            ordered.append(custom)
            seen.add(custom)
    return ordered


def _seed_list(current, defaults):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    if not values:
        return list(defaults)

    ordered = list(defaults)
    seen = set(ordered)
    for value in values:
        if value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def update_contract_config_fields(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        update_fields = [
            field
            for field in (
                "contract_type",
                "contract_standard",
                "commercial_model",
                "supporting_agreement",
            )
            if field in field_names
        ]
        if not update_fields:
            continue

        to_update = []
        for obj in model.objects.all().only("id", *update_fields):
            changed = False
            if "contract_type" in update_fields:
                current = list(getattr(obj, "contract_type", []) or [])
                updated = _normalize_contract_types(current)
                if updated != current:
                    obj.contract_type = updated
                    changed = True
            if "contract_standard" in update_fields:
                current = list(getattr(obj, "contract_standard", []) or [])
                updated = _seed_list(current, NEW_CONTRACT_STANDARDS)
                if updated != current:
                    obj.contract_standard = updated
                    changed = True
            if "commercial_model" in update_fields:
                current = list(getattr(obj, "commercial_model", []) or [])
                updated = _seed_list(current, NEW_COMMERCIAL_MODELS)
                if updated != current:
                    obj.commercial_model = updated
                    changed = True
            if "supporting_agreement" in update_fields:
                current = list(getattr(obj, "supporting_agreement", []) or [])
                updated = _seed_list(current, NEW_SUPPORTING_AGREEMENTS)
                if updated != current:
                    obj.supporting_agreement = updated
                    changed = True
            if changed:
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0100_document_review_and_transmittal_configs"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalconfig",
            name="contract_standard",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="globalconfig",
            name="commercial_model",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="globalconfig",
            name="supporting_agreement",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="contract_standard",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="commercial_model",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="companyconfig",
            name="supporting_agreement",
            field=ArrayField(
                base_field=models.CharField(max_length=255),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.RunPython(
            update_contract_config_fields,
            migrations.RunPython.noop,
        ),
    ]
