from django.db import migrations

NEW_COMPANY_DOCUMENT_TYPES = [
    "Bonds:BND",
    "Calculation:CAL",
    "Cash Flow Statement:CFS",
    "Change/Variation:CVR",
    "Claims/extension:CLX",
    "Collateral Warranty:CWA",
    "Contractor Initiated Changes:CIC",
    "Contractual Correspondence and Notices:CCN",
    "Coordination Meetings:CME",
    "CTS:CTS",
    "Data Sheet:DSH",
    "Drawing:DRW",
    "Employer's Instructions:EIN",
    "Final Payment:FPA",
    "General:GEN",
    "Hand-over:HOV",
    "HES - PD:HES",
    "Insurance:INS",
    "Interim Payment App. / Payment Notice:IPA",
    "Letter:LTR",
    "Loss and Expense Claim:LEC",
    "MOM:MOM",
    "MSDS:MSD",
    "Programme:PRG",
    "Progress Reports:PRR",
    "Punch list:PUL",
    "Quality Control Surv.:QCS",
    "Rectification Period:RCP",
    "RFI:RFI",
    "Schedule:SCH",
    "Single Line Diagram:SLD",
    "Specification:SPE",
    "Statutory Approval or Permissions:SAP",
    "Steering Committee Meeting:SCM",
]

NEW_LABELS = {item.split(":")[0] for item in NEW_COMPANY_DOCUMENT_TYPES}


def _normalize_company_document_types(current):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    customs = []
    for item in values:
        label = item.split(":")[0].strip()
        if label in NEW_LABELS:
            continue
        customs.append(item)

    ordered = list(NEW_COMPANY_DOCUMENT_TYPES)
    seen = set(ordered)
    seen_labels = set(NEW_LABELS)
    for custom in customs:
        custom_label = custom.split(":")[0].strip()
        if custom not in seen and custom_label not in seen_labels:
            ordered.append(custom)
            seen.add(custom)
            seen_labels.add(custom_label)
    return ordered


def add_document_type_codes(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        model = apps.get_model("models", model_name)
        field_names = {field.name for field in model._meta.get_fields()}
        if "document_types" not in field_names:
            continue

        to_update = []
        for obj in model.objects.all().only("id", "document_types"):
            current = list(getattr(obj, "document_types", []) or [])
            updated = _normalize_company_document_types(current)
            if updated != current:
                obj.document_types = updated
                to_update.append(obj)

        if to_update:
            model.objects.bulk_update(to_update, ["document_types"])


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0097_replace_team_members_roles"),
    ]

    operations = [
        migrations.RunPython(
            add_document_type_codes,
            migrations.RunPython.noop,
        ),
    ]
