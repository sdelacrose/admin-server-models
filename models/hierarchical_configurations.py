from copy import deepcopy
from uuid import uuid4


DOCUMENT_DISCIPLINES_KEY = "document_disciplines"
AREA_OF_EXPERTISE_KEY = "area_of_expertise"


DEFAULT_DOCUMENT_DISCIPLINE_HIERARCHY = {
    "groups": [
        {
            "id": "construction-site-management",
            "label": "Construction & Site Management",
            "children": [
                {"id": "commissioning", "label": "Commissioning", "code": "CMS"},
                {"id": "construction-management", "label": "Construction Management", "code": "CON"},
                {"id": "erection-installation", "label": "Erection / Installation", "code": "INS"},
                {"id": "field-engineering", "label": "Field Engineering", "code": "FIE"},
                {"id": "handover-close-out", "label": "Handover & Close-out", "code": "HAC"},
                {"id": "site-management", "label": "Site Management", "code": "SIM"},
            ],
        },
        {
            "id": "support-organization",
            "label": "Corporate Functions",
            "children": [
                {"id": "communication", "label": "Communication", "code": "COM"},
                {"id": "corporate-governance", "label": "Corporate Governance", "code": "GOV"},
                {"id": "human-resources", "label": "Human Resources", "code": "HRM"},
                {"id": "legal", "label": "Legal", "code": "LEG"},
                {"id": "organization", "label": "Organization", "code": "ORG"},
                {"id": "training-competency", "label": "Training & Competency", "code": "TRC"},
            ],
        },
        {
            "id": "digital-information-systems",
            "label": "Digital & Information Management",
            "children": [
                {"id": "bim-digital-engineering", "label": "BIM / Digital Engineering", "code": "BIM"},
                {"id": "document-control", "label": "Document Control", "code": "DOC"},
                {"id": "it-digital-systems", "label": "IT / Digital Systems", "code": "ITS"},
                {"id": "project-information-management", "label": "Project Information Management", "code": "PIM"},
            ],
        },
        {
            "id": "engineering",
            "label": "Engineering",
            "children": [
                {"id": "architecture", "label": "Architecture", "code": "ARC"},
                {"id": "civil-engineering", "label": "Civil Engineering", "code": "CIV"},
                {"id": "electrical-engineering", "label": "Electrical Engineering", "code": "ELE"},
                {"id": "industrial-engineering", "label": "Industrial Engineering", "code": "INE"},
                {"id": "instrumentation-control", "label": "Instrumentation & Control (I&C)", "code": "INC"},
                {"id": "mechanical-engineering", "label": "Mechanical Engineering", "code": "MEC"},
                {"id": "piping-engineering", "label": "Piping Engineering", "code": "PIP"},
                {"id": "process-engineering", "label": "Process Engineering", "code": "PRO"},
                {"id": "structural-engineering", "label": "Structural Engineering", "code": "STR"},
                {"id": "systems-engineering", "label": "Systems Engineering", "code": "SYE"},
                {"id": "telecommunications", "label": "Telecommunications", "code": "TEL"},
            ],
        },
        {
            "id": "finance-business",
            "label": "Finance & Business",
            "children": [
                {"id": "business-management", "label": "Business Management", "code": "BUM"},
                {"id": "commercial-management", "label": "Commercial Management", "code": "CMM"},
                {"id": "finance-controlling", "label": "Finance / Controlling", "code": "FIN"},
            ],
        },
        {
            "id": "operations-maintenance",
            "label": "Operations & Maintenance",
            "children": [
                {"id": "maintenance-engineering", "label": "Maintenance Engineering", "code": "MAE"},
                {"id": "operations", "label": "Operations", "code": "OPS"},
                {"id": "reliability-asset-management", "label": "Reliability / Asset Management", "code": "RAM"},
            ],
        },
        {
            "id": "procurement-contracts",
            "label": "Procurement & Contracts",
            "children": [
                {"id": "claims-management", "label": "Claims Management", "code": "CLM"},
                {"id": "contract-management", "label": "Contract Management", "code": "CTM"},
                {"id": "procurement", "label": "Procurement", "code": "PRC"},
                {"id": "subcontract-management", "label": "Subcontract Management", "code": "SUB"},
            ],
        },
        {
            "id": "project-management",
            "label": "Project Management & Controls",
            "children": [
                {"id": "cost-control", "label": "Cost Control", "code": "COC"},
                {"id": "estimating", "label": "Estimating", "code": "EST"},
                {"id": "interface-management", "label": "Interface management", "code": "IFM"},
                {"id": "planning-scheduling", "label": "Planning & Scheduling", "code": "SCH"},
                {"id": "pmo-governance", "label": "PMO / Governance", "code": "PMO"},
                {"id": "project-change-management", "label": "Project Change Management", "code": "PCM"},
                {"id": "project-controls", "label": "Project Controls", "code": "PCT"},
                {"id": "project-management-project-management", "label": "Project Management", "code": "PRM"},
                {"id": "risk-management", "label": "Risk Management", "code": "ESK"},
            ],
        },
        {
            "id": "quality-hse-compliance",
            "label": "Quality, HSE & Compliance",
            "children": [
                {"id": "health-safety-environment", "label": "Health safety environment", "code": "HSE"},
                {"id": "process-safety", "label": "Process Safety", "code": "PRS"},
                {"id": "quality-assurance", "label": "Quality assurance", "code": "QAS"},
                {"id": "quality-control", "label": "Quality control", "code": "QCO"},
                {"id": "regulatory-compliance", "label": "Regulatory & Compliance", "code": "REG"},
            ],
        },
        {
            "id": "supply-chain-logistics",
            "label": "Supply Chain & Logistics",
            "children": [
                {"id": "logistics", "label": "Logistics", "code": "LOG"},
                {"id": "materials-management", "label": "Materials Management", "code": "MAM"},
                {"id": "supply-chain-management", "label": "Supply Chain Management", "code": "SCM"},
            ],
        },
        {
            "id": "other",
            "label": "Other",
            "children": [
                {
                    "id": "legacy-other",
                    "label": "Other",
                    "code": "OTH",
                }
            ],
        },
    ]
}


DEFAULT_AREA_OF_EXPERTISE_HIERARCHY = {
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


DEFAULT_NESTED_CONFIGURATIONS = {
    DOCUMENT_DISCIPLINES_KEY: DEFAULT_DOCUMENT_DISCIPLINE_HIERARCHY,
    AREA_OF_EXPERTISE_KEY: DEFAULT_AREA_OF_EXPERTISE_HIERARCHY,
}

NESTED_CONFIGURATION_DEFINITIONS = {
    DOCUMENT_DISCIPLINES_KEY: {"child_code_required": True},
    AREA_OF_EXPERTISE_KEY: {"child_code_required": False},
}


class HierarchicalConfigurationError(ValueError):
    pass


def get_default_nested_configurations():
    return deepcopy(DEFAULT_NESTED_CONFIGURATIONS)


def get_default_nested_configuration(config_key):
    try:
        return deepcopy(DEFAULT_NESTED_CONFIGURATIONS[config_key])
    except KeyError as exc:
        raise HierarchicalConfigurationError(
            f"Unsupported nested configuration: {config_key}."
        ) from exc


def _required_text(value, field_name):
    normalized = str(value or "").strip()
    if not normalized:
        raise HierarchicalConfigurationError(f"{field_name} is required.")
    return normalized


def _node_id(value):
    normalized = str(value or "").strip()
    return normalized or f"custom-{uuid4()}"


def _default_indexes(config_key):
    default = get_default_nested_configuration(config_key)
    groups = {group["id"]: group for group in default["groups"]}
    child_parents = {}
    children = {}
    for group in default["groups"]:
        for child in group["children"]:
            child_parents[child["id"]] = group["id"]
            children[child["id"]] = child
    return groups, children, child_parents


def normalize_nested_configuration(
    config_key,
    configuration,
    *,
    existing_configuration=None,
    enforce_defaults=True,
):
    definition = NESTED_CONFIGURATION_DEFINITIONS.get(config_key)
    if definition is None:
        raise HierarchicalConfigurationError(
            f"Unsupported nested configuration: {config_key}."
        )
    if not isinstance(configuration, dict):
        raise HierarchicalConfigurationError("Configuration must be an object.")

    raw_groups = configuration.get("groups")
    if not isinstance(raw_groups, list):
        raise HierarchicalConfigurationError("Configuration groups must be a list.")

    normalized_groups = []
    group_ids = set()
    group_labels = set()
    child_ids = set()
    child_labels = set()
    child_codes = set()

    for raw_group in raw_groups:
        if not isinstance(raw_group, dict):
            raise HierarchicalConfigurationError("Each group must be an object.")

        group_id = _node_id(raw_group.get("id"))
        group_label = _required_text(raw_group.get("label"), "Group label")
        normalized_group_label = group_label.casefold()
        if group_id in group_ids or group_id in child_ids:
            raise HierarchicalConfigurationError(f"Duplicate node id: {group_id}.")
        if normalized_group_label in group_labels:
            raise HierarchicalConfigurationError(
                f"Duplicate group label: {group_label}."
            )

        raw_children = raw_group.get("children", [])
        if not isinstance(raw_children, list):
            raise HierarchicalConfigurationError(
                f"Children for {group_label} must be a list."
            )

        group_ids.add(group_id)
        group_labels.add(normalized_group_label)
        normalized_children = []
        sibling_labels = set()
        for raw_child in raw_children:
            if not isinstance(raw_child, dict):
                raise HierarchicalConfigurationError("Each child must be an object.")

            child_id = _node_id(raw_child.get("id"))
            child_label = _required_text(raw_child.get("label"), "Child label")
            normalized_child_label = child_label.casefold()
            if child_id in child_ids or child_id in group_ids:
                raise HierarchicalConfigurationError(f"Duplicate node id: {child_id}.")
            if normalized_child_label in sibling_labels or (
                config_key == DOCUMENT_DISCIPLINES_KEY
                and normalized_child_label in child_labels
            ):
                raise HierarchicalConfigurationError(
                    f"Duplicate child label: {child_label}."
                )

            normalized_child = {"id": child_id, "label": child_label}
            if definition["child_code_required"]:
                child_code = _required_text(raw_child.get("code"), "Child code").upper()
                if child_code in child_codes:
                    raise HierarchicalConfigurationError(
                        f"Duplicate child code: {child_code}."
                    )
                child_codes.add(child_code)
                normalized_child["code"] = child_code

            child_ids.add(child_id)
            child_labels.add(normalized_child_label)
            sibling_labels.add(normalized_child_label)
            normalized_children.append(normalized_child)

        normalized_group = {
            "id": group_id,
            "label": group_label,
            "children": normalized_children,
        }
        normalized_groups.append(normalized_group)

    normalized = {"groups": normalized_groups}
    if enforce_defaults:
        _validate_required_defaults(config_key, normalized)
    if existing_configuration:
        _validate_child_parents(existing_configuration, normalized)
    return normalized


def _validate_required_defaults(config_key, configuration):
    default_groups, default_children, default_child_parents = _default_indexes(config_key)
    submitted_groups = {group["id"]: group for group in configuration["groups"]}
    submitted_child_parents = {}
    submitted_children = {}
    for group in configuration["groups"]:
        for child in group["children"]:
            submitted_child_parents[child["id"]] = group["id"]
            submitted_children[child["id"]] = child

    for group_id, default_group in default_groups.items():
        submitted_group = submitted_groups.get(group_id)
        if submitted_group is None:
            raise HierarchicalConfigurationError(
                f"Default group cannot be removed: {default_group['label']}."
            )
        if submitted_group["label"] != default_group["label"]:
            raise HierarchicalConfigurationError(
                f"Default group cannot be renamed: {default_group['label']}."
            )
    for child_id, default_child in default_children.items():
        submitted_child = submitted_children.get(child_id)
        if submitted_child is None:
            raise HierarchicalConfigurationError(
                f"Default child cannot be removed: {default_child['label']}."
            )
        if submitted_child != default_child:
            raise HierarchicalConfigurationError(
                f"Default child cannot be edited: {default_child['label']}."
            )
        if submitted_child_parents[child_id] != default_child_parents[child_id]:
            raise HierarchicalConfigurationError(
                f"Default child cannot be moved: {default_child['label']}."
            )


def _validate_child_parents(existing_configuration, submitted_configuration):
    existing_parents = {
        child["id"]: group["id"]
        for group in existing_configuration.get("groups", [])
        for child in group.get("children", [])
        if isinstance(child, dict) and child.get("id")
    }
    for group in submitted_configuration["groups"]:
        for child in group["children"]:
            previous_parent = existing_parents.get(child["id"])
            if previous_parent and previous_parent != group["id"]:
                raise HierarchicalConfigurationError(
                    f"Child cannot be moved to another group: {child['label']}."
                )


def flatten_nested_configuration(config_key, configuration):
    normalized = normalize_nested_configuration(config_key, configuration)
    if config_key == DOCUMENT_DISCIPLINES_KEY:
        return [
            f"{child['label']}:{child['code']}"
            for group in normalized["groups"]
            for child in group["children"]
        ]
    values = []
    seen = set()
    for group in normalized["groups"]:
        for child in group["children"]:
            if child["label"] not in seen:
                values.append(child["label"])
                seen.add(child["label"])
    return values


def annotate_default_nodes(config_key, configuration):
    normalized = normalize_nested_configuration(config_key, configuration)
    default_groups, default_children, _ = _default_indexes(config_key)
    annotated = deepcopy(normalized)
    for group in annotated["groups"]:
        group["is_default"] = group["id"] in default_groups
        for child in group["children"]:
            child["is_default"] = child["id"] in default_children
    return annotated


def merge_nested_configurations(current, updates):
    if not isinstance(updates, dict):
        raise HierarchicalConfigurationError("Nested configuration updates must be an object.")

    merged = deepcopy(current) if isinstance(current, dict) else {}
    for config_key, configuration in updates.items():
        merged[config_key] = normalize_nested_configuration(
            config_key,
            configuration,
            existing_configuration=merged.get(config_key),
        )
    return merged


def resolve_nested_configurations(configurations):
    """Return a complete, normalized hierarchy while preserving future keys."""
    resolved = deepcopy(configurations) if isinstance(configurations, dict) else {}
    for config_key, default_configuration in DEFAULT_NESTED_CONFIGURATIONS.items():
        configuration = resolved.get(config_key, default_configuration)
        resolved[config_key] = normalize_nested_configuration(
            config_key,
            configuration,
        )
    return resolved


def flatten_nested_configurations(configurations):
    resolved = resolve_nested_configurations(configurations)
    return {
        config_key: flatten_nested_configuration(config_key, resolved[config_key])
        for config_key in DEFAULT_NESTED_CONFIGURATIONS
    }


def get_default_nested_configuration_values():
    nested = get_default_nested_configurations()
    return nested, flatten_nested_configurations(nested)


def prepare_nested_configurations_update(current, updates):
    merged = merge_nested_configurations(
        resolve_nested_configurations(current),
        updates,
    )
    return merged, flatten_nested_configurations(merged)


def annotate_nested_configurations(configurations):
    resolved = resolve_nested_configurations(configurations)
    annotated = deepcopy(resolved)
    for config_key in DEFAULT_NESTED_CONFIGURATIONS:
        annotated[config_key] = annotate_default_nodes(
            config_key,
            resolved[config_key],
        )
    return annotated
