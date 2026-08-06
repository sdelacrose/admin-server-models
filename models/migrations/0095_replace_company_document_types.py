from django.db import migrations

NEW_COMPANY_DOCUMENT_TYPES = [
    "Bonds",
    "Calculation",
    "Cash Flow Statement",
    "Change/Variation",
    "Claims/extension",
    "Collateral Warranty",
    "Contractor Initiated Changes",
    "Contractual Correspondence and Notices",
    "Coordination Meetings",
    "CTS",
    "Data Sheet",
    "Drawing",
    "Employer's Instructions",
    "Final Payment",
    "General",
    "Hand-over",
    "HES - PD",
    "Insurance",
    "Interim Payment App. / Payment Notice",
    "Letter",
    "Loss and Expense Claim",
    "MOM",
    "MSDS",
    "Programme",
    "Progress Reports",
    "Punch list",
    "Quality Control Surv.",
    "Rectification Period",
    "RFI",
    "Schedule",
    "Single Line Diagram",
    "Specification",
    "Statutory Approval or Permissions",
    "Steering Committee Meeting",
]

LEGACY_DEFAULT_DOCUMENT_TYPES = {
    "Supplier Invoice:SIN",
    "Customer Invoice:CIN",
    "Contract:CON",
    "Specification:SPE",
    "Funding Request:FUR",
    "Confirmation of Receipt:COR",
    "Funding Authorisation:FAU",
    "Drawing:DRW",
    "Report:RPT",
    "Manual:MAN",
    "Procedure:PRO",
    "Customer Demand:CDE",
    "Other:OTH",
    "Calendar:CAL",
    "Revision:REV",
    "Supplier Invoice",
    "Customer Invoice",
    "Contract",
    "Specification",
    "Funding Request",
    "Confirmation of Receipt",
    "Funding Authorisation",
    "Drawing",
    "Report",
    "Manual",
    "Procedure",
    "Customer Demand",
    "Other",
    "Calendar",
    "Revision",
}


def _normalize_company_document_types(current):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    customs = []
    for item in values:
        label = item.split(":")[0].strip()
        if item in LEGACY_DEFAULT_DOCUMENT_TYPES or label in LEGACY_DEFAULT_DOCUMENT_TYPES:
            continue
        if item not in NEW_COMPANY_DOCUMENT_TYPES and label not in NEW_COMPANY_DOCUMENT_TYPES:
            customs.append(item)

    ordered = list(NEW_COMPANY_DOCUMENT_TYPES)
    seen = set(ordered)
    for custom in customs:
        if custom not in seen:
            ordered.append(custom)
            seen.add(custom)
    return ordered


def replace_company_document_types(apps, schema_editor):
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
        ("models", "0094_remove_general_tasks"),
    ]

    operations = [
        migrations.RunPython(
            replace_company_document_types,
            migrations.RunPython.noop,
        ),
    ]
