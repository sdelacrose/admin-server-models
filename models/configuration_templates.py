from copy import deepcopy

from . import constants
from .hierarchical_configurations import (
    DOCUMENT_DISCIPLINES_KEY,
    flatten_nested_configurations,
    get_default_nested_configurations,
    resolve_nested_configurations,
)


PLAIN_FIELD_KIND = "plain"
CODED_FIELD_KIND = "coded"
STATUS_FIELD_KIND = "status"

PROJECT_DEMAND_STATUS_OPTIONS = [
    "open:#99dce8",
    "in progress:#fff3ad",
    "closed:#bdefe0",
]
PROJECT_REQUIREMENT_STATUS_OPTIONS = list(PROJECT_DEMAND_STATUS_OPTIONS)
PROJECT_BOM_STATUS_OPTIONS = list(PROJECT_DEMAND_STATUS_OPTIONS)

COMPANY_CONFIGURATION_FIELDS = (
    "contract_type",
    "international_standard",
    "major_project_model",
    "commercial_model",
    "supporting_agreement",
    "team_members_roles",
    "company_roles",
    "funding_strategy",
    "status_options",
    "reminder_settings",
    "invoice_status",
    "expense_types",
    "project_types",
    "document_types",
    "document_status",
    "document_internal_review_status",
    "document_external_review_status",
    "transmittal_category",
    "priority_levels",
    "project_priority_levels",
    "leave_types",
    "opportunity_sales_phase",
    "offer_validity_periods",
    "project_service_types",
    "labels",
    "purchase_order_status",
    "document_categories",
    "document_disciplines",
    "nested_configurations",
    "configuration_visibility",
    "rooms",
    "skills",
)

# This registry intentionally matches the existing Project Configuration UI.
PROJECT_CONFIGURATION_FIELDS = (
    "status_options",
    "team_members_roles",
    "funding_strategy",
    "reminder_settings",
    "document_types",
    "document_status",
    "document_internal_review_status",
    "document_external_review_status",
    "transmittal_category",
    "priority_levels",
    "project_service_types",
    "labels",
    "document_disciplines",
    "document_categories",
    "skills",
    "demand_status_options",
    "requirement_status_options",
    "bom_status_options",
    "nested_configurations",
)

NESTED_DERIVED_FIELDS = {
    DOCUMENT_DISCIPLINES_KEY: "document_disciplines",
}

STATUS_CONFIGURATION_FIELDS = frozenset(
    {
        "status_options",
        "demand_status_options",
        "requirement_status_options",
        "bom_status_options",
    }
)
CODED_CONFIGURATION_FIELDS = frozenset(
    {
        "document_types",
        "document_categories",
        "document_disciplines",
    }
)


def configuration_field_kind(field_name):
    if field_name in STATUS_CONFIGURATION_FIELDS:
        return STATUS_FIELD_KIND
    if field_name in CODED_CONFIGURATION_FIELDS:
        return CODED_FIELD_KIND
    return PLAIN_FIELD_KIND


def get_company_configuration_defaults():
    nested = get_default_nested_configurations()
    flattened = flatten_nested_configurations(nested)
    return {
        "contract_type": list(constants.GC_CONTRACT_TYPES),
        "international_standard": list(constants.GC_INTERNATIONAL_STANDARDS),
        "major_project_model": list(constants.GC_MAJOR_PROJECT_MODELS),
        "commercial_model": list(constants.GC_COMMERCIAL_MODELS),
        "supporting_agreement": list(constants.GC_SUPPORTING_AGREEMENTS),
        "team_members_roles": list(constants.GC_TEAM_MEMBERS_ROLES),
        "company_roles": list(constants.GC_COMPANY_ROLES),
        "funding_strategy": list(constants.GC_FUNDING_STRATEGY),
        "status_options": list(constants.GC_STATUS_OPTIONS),
        "reminder_settings": list(constants.GC_REMINDER_SETTINGS),
        "invoice_status": list(constants.GC_INVOICE_STATUS),
        "expense_types": list(constants.GC_EXPENSE_TYPES),
        "project_types": list(constants.GC_PROJECT_TYPES),
        "document_types": list(constants.GC_COMPANY_DOCUMENT_TYPES),
        "document_status": list(constants.GC_DOCUMENT_STATUSES),
        "document_internal_review_status": list(
            constants.GC_DOCUMENT_INTERNAL_REVIEW_STATUSES
        ),
        "document_external_review_status": list(
            constants.GC_DOCUMENT_EXTERNAL_REVIEW_STATUSES
        ),
        "transmittal_category": list(constants.GC_TRANSMITTAL_CATEGORIES),
        "priority_levels": list(constants.GC_PRIORITY_LEVELS),
        "project_priority_levels": list(constants.GC_PROJECT_PRIORITY_LEVELS),
        "leave_types": list(constants.GC_LEAVE_TYPES),
        "opportunity_sales_phase": list(constants.GC_OPPORTUNITY_SALES_PHASE),
        "offer_validity_periods": [],
        "project_service_types": list(constants.GC_PROJECT_SERVICE_TYPES),
        "labels": [],
        "purchase_order_status": list(constants.GC_PURCHASE_ORDER_STATUS),
        "document_categories": list(constants.GC_DOCUMENT_CATEGORIES),
        "document_disciplines": flattened[DOCUMENT_DISCIPLINES_KEY],
        "nested_configurations": nested,
        "configuration_visibility": {},
        "rooms": list(constants.GC_ROOMS),
        "skills": list(constants.GC_SKILLS),
    }


def _canonical_project_defaults():
    nested = {
        DOCUMENT_DISCIPLINES_KEY: get_default_nested_configurations()[
            DOCUMENT_DISCIPLINES_KEY
        ]
    }
    flattened = flatten_nested_configurations(nested)
    return {
        "team_members_roles": list(constants.GC_TEAM_MEMBERS_ROLES),
        "funding_strategy": list(constants.GC_FUNDING_STRATEGY),
        "status_options": list(constants.GC_STATUS_OPTIONS),
        "demand_status_options": list(PROJECT_DEMAND_STATUS_OPTIONS),
        "requirement_status_options": list(PROJECT_REQUIREMENT_STATUS_OPTIONS),
        "bom_status_options": list(PROJECT_BOM_STATUS_OPTIONS),
        "reminder_settings": list(constants.GC_REMINDER_SETTINGS),
        "document_types": list(constants.GC_PROJECT_DOCUMENT_TYPES),
        "document_status": list(constants.GC_DOCUMENT_STATUSES),
        "document_internal_review_status": list(
            constants.GC_DOCUMENT_INTERNAL_REVIEW_STATUSES
        ),
        "document_external_review_status": list(
            constants.GC_DOCUMENT_EXTERNAL_REVIEW_STATUSES
        ),
        "transmittal_category": list(constants.GC_TRANSMITTAL_CATEGORIES),
        "priority_levels": list(constants.GC_PRIORITY_LEVELS),
        "project_service_types": list(constants.GC_PROJECT_SERVICE_TYPES),
        "labels": [],
        "document_categories": list(constants.GC_DOCUMENT_CATEGORIES),
        "document_disciplines": flattened[DOCUMENT_DISCIPLINES_KEY],
        "nested_configurations": nested,
        "skills": list(constants.GC_SKILLS),
    }


def get_project_template_defaults(source=None):
    """Build an independent project template, optionally seeded from GlobalConfig."""

    defaults = _canonical_project_defaults()
    if source is None:
        return defaults

    project_specific_fields = {
        "document_types",
        "demand_status_options",
        "requirement_status_options",
        "bom_status_options",
    }
    for field_name in PROJECT_CONFIGURATION_FIELDS:
        if field_name in project_specific_fields:
            continue
        if hasattr(source, field_name):
            defaults[field_name] = deepcopy(getattr(source, field_name))

    nested = resolve_nested_configurations(defaults["nested_configurations"])
    nested = {DOCUMENT_DISCIPLINES_KEY: nested[DOCUMENT_DISCIPLINES_KEY]}
    flattened = flatten_nested_configurations(nested)
    defaults["nested_configurations"] = nested
    for config_key, field_name in NESTED_DERIVED_FIELDS.items():
        defaults[field_name] = flattened[config_key]
    return defaults
