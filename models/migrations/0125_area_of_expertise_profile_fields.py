from copy import deepcopy

from django.db import migrations, models


AREA_OF_EXPERTISE_KEY = "area_of_expertise"
AREA_OF_EXPERTISE_HIERARCHY_V1 = {
    "groups": [
        {
            "id": "project-program-management",
            "label": "Project & Program Management",
            "children": [
                {"id": "expertise-project-management", "label": "Project Management"},
                {"id": "program-management", "label": "Program Management"},
                {"id": "portfolio-management-ppm", "label": "Portfolio Management (PPM)"},
                {"id": "pmo", "label": "PMO"},
                {"id": "expertise-planning-scheduling", "label": "Planning & Scheduling"},
                {"id": "cost-control-engineering", "label": "Cost Control / Cost Engineering"},
                {"id": "risk-management", "label": "Risk Management"},
                {"id": "expertise-change-management", "label": "Change Control Management"},
                {"id": "earned-value-management", "label": "Earned Value Management (EVM)"},
                {"id": "stakeholder-management", "label": "Stakeholder Management"},
                {"id": "documentation-management", "label": "Documentation Management"},
            ],
        },
        {
            "id": "engineering-technical-management",
            "label": "Engineering & Technical Management",
            "children": [
                {"id": "engineering-management", "label": "Engineering Management"},
                {"id": "expertise-systems-engineering", "label": "Systems Engineering"},
                {"id": "requirements-management", "label": "Requirements Management"},
                {"id": "interface-management", "label": "Interface Management"},
                {"id": "configuration-management", "label": "Configuration Management"},
                {"id": "design-coordination", "label": "Design Coordination"},
                {"id": "technical-documentation", "label": "Technical Documentation"},
                {"id": "validation-verification", "label": "Validation & Verification"},
            ],
        },
        {
            "id": "expertise-construction-site-management",
            "label": "Construction & Site Management",
            "children": [
                {"id": "expertise-construction-management", "label": "Construction Management"},
                {"id": "expertise-site-management", "label": "Site Management"},
                {"id": "expertise-commissioning", "label": "Commissioning"},
                {"id": "expertise-handover-close-out", "label": "Handover & Close-out"},
                {"id": "expertise-field-engineering", "label": "Field Engineering"},
                {"id": "workface-planning", "label": "Workface Planning"},
                {"id": "authorities-permits", "label": "Authorities & Permits"},
            ],
        },
        {
            "id": "procurement-contracts-claims",
            "label": "Procurement, Contracts & Claims",
            "children": [
                {"id": "expertise-procurement", "label": "Procurement"},
                {"id": "supplier-management", "label": "Supplier Management"},
                {"id": "expertise-subcontract-management", "label": "Subcontract Management"},
                {"id": "expertise-contract-management", "label": "Contract Management"},
                {"id": "tendering-bids-management", "label": "Tendering / Bids Management"},
                {"id": "contract-administration", "label": "Contract Administration"},
                {"id": "expertise-claims-management", "label": "Claims Management"},
            ],
        },
        {
            "id": "expertise-quality-hse-compliance",
            "label": "Quality, HSE & Compliance",
            "children": [
                {"id": "quality-management-qa-qc", "label": "Quality Management (QA/QC)"},
                {"id": "inspections", "label": "Inspections"},
                {"id": "audits", "label": "Audits"},
                {"id": "hse-management", "label": "HSE Management"},
                {"id": "safety", "label": "Safety"},
                {"id": "regulatory-compliance", "label": "Regulatory Compliance"},
                {"id": "sustainability", "label": "Sustainability"},
            ],
        },
        {
            "id": "expertise-operations-maintenance",
            "label": "Operations & Maintenance",
            "children": [
                {"id": "operations-management", "label": "Operations Management"},
                {"id": "maintenance-management", "label": "Maintenance Management"},
                {"id": "asset-management", "label": "Asset Management"},
                {"id": "reliability-engineering", "label": "Reliability Engineering"},
                {"id": "predictive-maintenance", "label": "Predictive Maintenance"},
            ],
        },
        {
            "id": "manufacturing-industrial-performance",
            "label": "Manufacturing & Industrial Performance",
            "children": [
                {"id": "production-management", "label": "Production Management"},
                {"id": "lean-manufacturing", "label": "Lean Manufacturing"},
                {"id": "continuous-improvement", "label": "Continuous Improvement"},
                {"id": "expertise-industrial-engineering", "label": "Industrial Engineering"},
                {"id": "performance-management-oee", "label": "Performance Management (OEE)"},
            ],
        },
        {
            "id": "expertise-supply-chain-logistics",
            "label": "Supply Chain & Logistics",
            "children": [
                {"id": "expertise-supply-chain-management", "label": "Supply Chain Management"},
                {"id": "expertise-logistics", "label": "Logistics"},
                {"id": "expertise-materials-management", "label": "Materials Management"},
                {"id": "inventory-management", "label": "Inventory Management"},
                {"id": "warehousing", "label": "Warehousing"},
                {"id": "transport-customs", "label": "Transport & Customs"},
            ],
        },
        {
            "id": "digital-data-project-tools",
            "label": "Digital, Data & Project Tools",
            "children": [
                {"id": "expertise-project-information-management", "label": "Project Information Management"},
                {"id": "bim-management", "label": "BIM Management"},
                {"id": "erp-mes-cmms", "label": "ERP / MES / CMMS"},
                {"id": "data-analysis-bi", "label": "Data Analysis & BI"},
                {"id": "digital-transformation", "label": "Digital Transformation"},
                {"id": "workflow-automation", "label": "Workflow Automation"},
            ],
        },
        {
            "id": "finance-commercial-management",
            "label": "Finance & Commercial Management",
            "children": [
                {"id": "project-finance", "label": "Project Finance"},
                {"id": "budgeting-forecasting", "label": "Budgeting & Forecasting"},
                {"id": "capex-opex-management", "label": "CAPEX / OPEX Management"},
                {"id": "business-case-roi", "label": "Business Case & ROI"},
                {"id": "controlling", "label": "Controlling"},
                {"id": "expertise-commercial-management", "label": "Commercial Management"},
            ],
        },
        {
            "id": "people-organization-change",
            "label": "People, Organization & Change",
            "children": [
                {"id": "organizational-design", "label": "Organizational Design"},
                {"id": "workforce-planning", "label": "Workforce Planning"},
                {"id": "expertise-training-competency", "label": "Training & Competency"},
                {"id": "people-change-management", "label": "Organizational Change Management"},
                {"id": "transformation-programs", "label": "Transformation Programs"},
                {"id": "communication-management", "label": "Communication Management"},
            ],
        },
        {
            "id": "industry-sector-expertise",
            "label": "Industry / Sector Expertise",
            "children": [
                {"id": "energy-power", "label": "Energy & Power"},
                {"id": "renewables", "label": "Renewables"},
                {"id": "oil-gas", "label": "Oil & Gas"},
                {"id": "nuclear", "label": "Nuclear"},
                {"id": "chemicals-pharma", "label": "Chemicals / Pharma"},
                {"id": "automotive", "label": "Automotive"},
                {"id": "aerospace-defense", "label": "Aerospace & Defense"},
                {"id": "rail-mobility", "label": "Rail & Mobility"},
                {"id": "marine-offshore", "label": "Marine / Offshore"},
                {"id": "data-centers", "label": "Data Centers"},
            ],
        },
    ]
}


def _known_ids(values, allowed_ids):
    if not isinstance(values, list):
        return []
    return [
        value
        for value in values
        if isinstance(value, str) and value in allowed_ids
    ]


def _clean_area_of_expertise(
    nested_configurations,
    configuration_visibility,
    default_configuration,
):
    nested = (
        deepcopy(nested_configurations)
        if isinstance(nested_configurations, dict)
        else {}
    )
    visibility = (
        deepcopy(configuration_visibility)
        if isinstance(configuration_visibility, dict)
        else {}
    )

    nested[AREA_OF_EXPERTISE_KEY] = deepcopy(default_configuration)

    default_group_ids = {
        group["id"] for group in default_configuration.get("groups", [])
    }
    default_child_ids = {
        child["id"]
        for group in default_configuration.get("groups", [])
        for child in group.get("children", [])
    }
    current_area_visibility = visibility.get(AREA_OF_EXPERTISE_KEY, {})
    if not isinstance(current_area_visibility, dict):
        current_area_visibility = {}

    cleaned_area_visibility = {}
    disabled_group_ids = _known_ids(
        current_area_visibility.get("disabled_group_ids"),
        default_group_ids,
    )
    disabled_child_ids = _known_ids(
        current_area_visibility.get("disabled_child_ids"),
        default_child_ids,
    )
    if disabled_group_ids:
        cleaned_area_visibility["disabled_group_ids"] = disabled_group_ids
    if disabled_child_ids:
        cleaned_area_visibility["disabled_child_ids"] = disabled_child_ids

    if cleaned_area_visibility:
        visibility[AREA_OF_EXPERTISE_KEY] = cleaned_area_visibility
    else:
        visibility.pop(AREA_OF_EXPERTISE_KEY, None)

    return nested, visibility


def remove_custom_area_of_expertise_nodes(apps, schema_editor):
    for model_name in ("GlobalConfig", "CompanyConfig"):
        configuration_model = apps.get_model("models", model_name)
        for configuration in configuration_model.objects.iterator():
            nested, visibility = _clean_area_of_expertise(
                configuration.nested_configurations,
                configuration.configuration_visibility,
                AREA_OF_EXPERTISE_HIERARCHY_V1,
            )
            update_fields = []
            if nested != configuration.nested_configurations:
                configuration.nested_configurations = nested
                update_fields.append("nested_configurations")
            if visibility != configuration.configuration_visibility:
                configuration.configuration_visibility = visibility
                update_fields.append("configuration_visibility")
            if update_fields:
                configuration.save(update_fields=update_fields)


class Migration(migrations.Migration):
    dependencies = [
        ("models", "0124_display_configuration_registry_version_16"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="main_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="sub_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="main_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="companyprofile",
            name="sub_area_of_expertise",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(
            remove_custom_area_of_expertise_nodes,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
