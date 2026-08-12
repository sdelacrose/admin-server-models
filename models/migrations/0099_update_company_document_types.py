from django.db import migrations

NEW_COMPANY_DOCUMENT_TYPES = [
    "Bonds:BON",
    "Cash Flow Statement:SFS",
    "Change/Variation:CVA",
    "Claims/extensions:CEX",
    "Collateral Warranty:CW",
    "Contractor Initiated Changes:CIC",
    "Contractual Correspondence and Notices:CCN",
    "Coordination Meeting:COM",
    "Drawing:DRW",
    "Employer's Instructions:EIN",
    "Estimate, budget:EST",
    "Final Payment:FPA",
    "General:GEN",
    "Hand-over:HOV",
    "Insurance:INS",
    "Interim Payment App / Payment Notice:INP",
    "Letter:LET",
    "List of any kind, index, legend:LST",
    "Loss and Expense Claim:LEC",
    "Minutes of meeting:MOM",
    "Programme:PGM",
    "Progress Report:PRE",
    "Punch list:PUL",
    "Purchase order:PO",
    "Quality Control Surv:QCS",
    "Rectification Period:REP",
    "Schedule:SCH",
    "Statutory Approval or Permission:SAP",
    "Steering Committee Meeting:SCM",
    "Other:OTH",
]

NEW_LABELS = {item.rsplit(":", 1)[0] for item in NEW_COMPANY_DOCUMENT_TYPES}
NEW_CODES = {
    item.rsplit(":", 1)[1]
    for item in NEW_COMPANY_DOCUMENT_TYPES
    if ":" in item
}

PREVIOUS_DEFAULT_LABELS = {
    "Diagram; engineering, functional, block, interconnection, nodal, circuit",
    "Diagram: engineering, functional, block, interconnection, nodal, circuit",
    "Project control (MPR, Cost report, close-out report, etc)",
    "Project control (MPR, Cost report, close-out report, etc.)",
    "Org chart, functional descriptions etc",
    "Org. chart, functional descriptions etc.",
    "Operational information (eg Operating manual)",
    "Operational information (e.g. Operating manual)",
    "Maintenance information (eg Maintenance manual)",
    "Maintenance information (e.g. Maintenance manual)",
    "Layout of any kind (plot plan, site plan etc)",
    "Layout of any kind (plot plan, site plan etc.)",
    "Call for meeting, MoM, meeting presentation, etc",
    "Call for meeting, MoM, meeting presentation, etc.",
    "Quality Control Surv",
    "Interim Payment App / Payment Notice",
    "Bonds",
    "Calculation",
    "Cash Flow Statement",
    "Change/Variation",
    "Claims/extension",
    "Claims/extensions",
    "Collateral Warranty",
    "Contractor Initiated Changes",
    "Contractual Correspondence and Notices",
    "Coordination Meetings",
    "Coordination Meeting",
    "CTS",
    "Data Sheet",
    "Drawing",
    "Employer's Instructions",
    "Estimate, budget",
    "Final Payment",
    "General",
    "Hand-over",
    "HES - PD",
    "Insurance",
    "Interim Payment App. / Payment Notice",
    "Letter",
    "List of any kind, index, legend",
    "Loss and Expense Claim",
    "MOM",
    "Minutes of meeting",
    "MSDS",
    "Other",
    "Programme",
    "Progress Reports",
    "Progress Report",
    "Punch list",
    "Purchase order",
    "Quality Control Surv.",
    "Rectification Period",
    "RFI",
    "Schedule",
    "Single Line Diagram",
    "Specification",
    "Statutory Approval or Permissions",
    "Statutory Approval or Permission",
    "Steering Committee Meeting",
    "Supplier Invoice",
    "Customer Invoice",
    "Contract",
    "Funding Request",
    "Confirmation of Receipt",
    "Funding Authorisation",
    "Report",
    "Manual",
    "Procedure",
    "Customer Demand",
    "Calendar",
    "Revision",
}


def _split_label_code(item):
    if ":" not in item:
        return item.strip(), ""
    label, code = item.rsplit(":", 1)
    return label.strip(), code.strip()


def _normalize_company_document_types(current):
    values = [str(item).strip() for item in (current or []) if str(item).strip()]
    customs = []
    for item in values:
        label, code = _split_label_code(item)
        if label in NEW_LABELS or label in PREVIOUS_DEFAULT_LABELS:
            continue
        if code and code in NEW_CODES:
            continue
        customs.append(item)

    ordered = list(NEW_COMPANY_DOCUMENT_TYPES)
    seen = set(ordered)
    seen_labels = set(NEW_LABELS)
    for custom in customs:
        custom_label, _code = _split_label_code(custom)
        if custom not in seen and custom_label not in seen_labels:
            ordered.append(custom)
            seen.add(custom)
            seen_labels.add(custom_label)
    return ordered


def update_company_document_types(apps, schema_editor):
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
        ("models", "0098_add_document_type_codes"),
    ]

    operations = [
        migrations.RunPython(
            update_company_document_types,
            migrations.RunPython.noop,
        ),
    ]
