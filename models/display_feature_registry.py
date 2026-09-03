"""Canonical display-feature registry shared by the Admin and Core backends."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

from .constants import ADMIN_SERVER_MODULES, PROJECT_MODULES, SOLUTION_MODULES


DISPLAY_FEATURE_SCHEMA_MAJOR = 1
DISPLAY_FEATURE_REGISTRY_REVISION = 16
# Backward-compatible storage/API alias. New clients use schema/revision fields.
DISPLAY_FEATURE_REGISTRY_VERSION = DISPLAY_FEATURE_REGISTRY_REVISION


class SolutionId(str, Enum):
    ENERGY_CONSULTANT = "energy_consultant_solution"
    ENTERPRISE = "enterprise_solution"
    CORE = "core_solution"


class FeatureType(str, Enum):
    SECTION = "section"
    MODULE = "module"
    SUBMODULE = "submodule"
    TAB = "tab"
    LINKED_OBJECT = "linked_object"


class PermissionScope(str, Enum):
    COMPANY = "company"
    PROJECT = "project"


@dataclass(frozen=True)
class PermissionRule:
    scope: PermissionScope
    module: str
    actions: tuple[str, ...] = ("view",)
    require_all: bool = False


@dataclass(frozen=True)
class DisplayFeature:
    key: str
    feature_type: FeatureType
    label_key: str
    available_in: frozenset[SolutionId]
    parent_key: str | None = None
    default_visible: bool = True
    dependencies: tuple[str, ...] = ()
    permissions: tuple[PermissionRule, ...] = ()

    @property
    def permission(self) -> PermissionRule | None:
        """Retain the original API contract while permissions become composable."""
        return self.permissions[0] if self.permissions else None


class DisplayFeatureRegistryError(ValueError):
    """Raised when the canonical registry contains invalid relationships."""


ALL_SOLUTIONS = frozenset(SolutionId)
PROJECT_SOLUTIONS = frozenset(
    (SolutionId.ENERGY_CONSULTANT, SolutionId.ENTERPRISE)
)
ENERGY_ONLY = frozenset((SolutionId.ENERGY_CONSULTANT,))

_BACKEND_SOLUTION_TITLES = {
    "Energy Consultant Solution": SolutionId.ENERGY_CONSULTANT,
    "Enterprise Solution": SolutionId.ENTERPRISE,
    "Core Solution": SolutionId.CORE,
}

_LINKED_OBJECT_DEPENDENCIES = {
    "action_items": {
        PermissionScope.COMPANY: "company.action_items",
        PermissionScope.PROJECT: "project.action_items",
    },
    "available_product": {
        PermissionScope.COMPANY: "company.product_services.available_products",
        PermissionScope.PROJECT: "company.product_services.available_products",
    },
    "demands": {
        PermissionScope.PROJECT: "project.system_requirements.customer_demands",
    },
    "documents": {
        PermissionScope.COMPANY: "company.documents",
        PermissionScope.PROJECT: "project.documents",
    },
    "machines": {
        PermissionScope.COMPANY: "company.product_services.machines",
    },
    "observations": {
        PermissionScope.PROJECT: "project.object_assessment",
    },
    "opportunities": {
        PermissionScope.COMPANY: "company.opportunities_offers",
    },
    "projects": {
        PermissionScope.COMPANY: "company.projects",
    },
    "requirements": {
        PermissionScope.PROJECT: "project.system_requirements.technical_requirements",
    },
    "structure": {
        PermissionScope.COMPANY: "company.documents",
        PermissionScope.PROJECT: "project.documents",
    },
}


def permission(
    scope: PermissionScope,
    module: str,
    *actions: str,
    require_all: bool = False,
) -> PermissionRule:
    return PermissionRule(
        scope=scope,
        module=module,
        actions=tuple(actions) or ("view",),
        require_all=require_all,
    )


def _linked_dependencies(key: str) -> tuple[str, ...]:
    if ".linked." not in key:
        return ()

    linked_object = key.rsplit(".", 1)[-1]
    dependency_by_scope = _LINKED_OBJECT_DEPENDENCIES.get(linked_object)
    if not dependency_by_scope:
        return ()

    scope = (
        PermissionScope.PROJECT
        if key.startswith("project.")
        else PermissionScope.COMPANY
    )
    dependency = dependency_by_scope.get(scope)
    return (dependency,) if dependency else ()


def _feature(
    key: str,
    feature_type: FeatureType,
    *,
    parent_key: str | None = None,
    available_in: frozenset[SolutionId] = ALL_SOLUTIONS,
    default_visible: bool = True,
    dependencies: tuple[str, ...] | None = None,
    permission_rules: tuple[PermissionRule, ...] = (),
) -> DisplayFeature:
    return DisplayFeature(
        key=key,
        feature_type=feature_type,
        label_key=f"DisplayConfiguration.Features.{key}",
        available_in=available_in,
        parent_key=parent_key,
        default_visible=default_visible,
        dependencies=(
            _linked_dependencies(key) if dependencies is None else dependencies
        ),
        permissions=permission_rules,
    )


def _build_registry() -> tuple[DisplayFeature, ...]:
    features: list[DisplayFeature] = []

    def add(
        key: str,
        feature_type: FeatureType,
        *,
        parent: str | None = None,
        solutions: frozenset[SolutionId] = ALL_SOLUTIONS,
        permission_rule: PermissionRule | None = None,
        permission_rules: tuple[PermissionRule, ...] = (),
    ) -> None:
        resolved_parent = parent
        if resolved_parent is None and feature_type is not FeatureType.SECTION:
            if key.startswith("company."):
                resolved_parent = "company"
            elif key.startswith("project."):
                resolved_parent = "project"
        features.append(
            _feature(
                key,
                feature_type,
                parent_key=resolved_parent,
                available_in=solutions,
                permission_rules=(
                    permission_rules
                    if permission_rules
                    else ((permission_rule,) if permission_rule else ())
                ),
            )
        )

    company = PermissionScope.COMPANY
    project = PermissionScope.PROJECT

    add("company", FeatureType.SECTION)

    add(
        "company.dashboard",
        FeatureType.MODULE,
    )
    for tab in ("global_dashboard", "personal_dashboard", "reports"):
        add(
            f"company.dashboard.tabs.{tab}",
            FeatureType.TAB,
            parent="company.dashboard",
        )

    add(
        "company.action_items",
        FeatureType.MODULE,
        permission_rule=permission(company, "action_item"),
    )
    for tab in ("list", "board", "time", "calendar", "gantt"):
        add(
            f"company.action_items.tabs.{tab}",
            FeatureType.TAB,
            parent="company.action_items",
        )
    for linked_object in (
        "comments",
        "documents",
        "structure",
        "predecessors",
        "dependents",
        "opportunities",
    ):
        add(
            f"company.action_items.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent="company.action_items",
        )

    add(
        "company.calendar",
        FeatureType.MODULE,
        permission_rule=permission(company, "calendar_events"),
    )
    for linked_object in ("documents", "structure"):
        add(
            f"company.calendar.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent="company.calendar",
        )

    add(
        "company.documents",
        FeatureType.MODULE,
        permission_rule=permission(company, "documents"),
    )
    for tab in ("folder", "register"):
        add(
            f"company.documents.tabs.{tab}",
            FeatureType.TAB,
            parent="company.documents",
        )

    # Permission enforcement for AI Assistant remains intentionally deferred.
    add("company.ai_assistant", FeatureType.MODULE)

    add(
        "company.network",
        FeatureType.MODULE,
        permission_rule=permission(company, "contact_management"),
    )
    for tab in ("companies", "contacts"):
        add(
            f"company.network.tabs.{tab}",
            FeatureType.TAB,
            parent="company.network",
        )

    add("company.product_services", FeatureType.MODULE)
    add(
        "company.product_services.available_products",
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rule=permission(company, "available_product_parts"),
    )
    for linked_object in ("comments", "documents", "structure"):
        add(
            f"company.product_services.available_products.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent="company.product_services.available_products",
        )

    company_assembly_catalog = "company.product_services.assembly_catalog"
    add(
        company_assembly_catalog,
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rules=(
            permission(company, "company_assembly_catalog"),
            permission(company, "aas_models"),
        ),
    )
    for tab in (
        "list",
        "semantic",
        "knowledge_graph",
        "cad_model",
        "sysml_models",
        "aas_models",
    ):
        add(
            f"{company_assembly_catalog}.tabs.{tab}",
            FeatureType.TAB,
            parent=company_assembly_catalog,
            permission_rule=permission(
                company,
                (
                    "aas_models"
                    if tab == "aas_models"
                    else "company_assembly_catalog"
                ),
            ),
        )
    for linked_object in ("comments", "documents", "structure"):
        add(
            f"{company_assembly_catalog}.tabs.list.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=f"{company_assembly_catalog}.tabs.list",
        )

    services = "company.product_services.services"
    add(
        services,
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rule=permission(company, "projects"),
    )
    for tab in ("list", "search"):
        add(f"{services}.tabs.{tab}", FeatureType.TAB, parent=services)

    knowledge = "company.product_services.knowledge"
    add(
        knowledge,
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rule=permission(company, "projects"),
    )
    for tab in ("list", "search", "creation", "preparation", "sysml_models"):
        add(f"{knowledge}.tabs.{tab}", FeatureType.TAB, parent=knowledge)

    machines = "company.product_services.machines"
    add(
        machines,
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rule=permission(company, "machines"),
    )
    for linked_object in ("comments", "projects", "documents", "structure"):
        add(
            f"{machines}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=machines,
        )

    equipments = "company.product_services.equipments"
    add(
        equipments,
        FeatureType.SUBMODULE,
        parent="company.product_services",
        permission_rule=permission(company, "equipments"),
    )
    for linked_object in ("comments", "documents", "structure"):
        add(
            f"{equipments}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=equipments,
        )

    opportunities = "company.opportunities_offers"
    add(
        opportunities,
        FeatureType.MODULE,
        permission_rule=permission(company, "opportunity_offers"),
    )
    for tab in ("all", "opportunities", "offers"):
        add(f"{opportunities}.tabs.{tab}", FeatureType.TAB, parent=opportunities)
    for linked_object in ("action_items", "documents", "projects", "structure"):
        add(
            f"{opportunities}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=opportunities,
        )

    add(
        "company.projects",
        FeatureType.MODULE,
        permission_rule=permission(company, "projects"),
    )
    for tab in ("list", "kanban", "gantt"):
        add(
            f"company.projects.tabs.{tab}",
            FeatureType.TAB,
            parent="company.projects",
        )
    add(
        "company.projects.linked.machines",
        FeatureType.LINKED_OBJECT,
        parent="company.projects",
    )
    add("company.financial", FeatureType.MODULE)
    purchase_orders = "company.financial.purchase_orders"
    add(
        purchase_orders,
        FeatureType.SUBMODULE,
        parent="company.financial",
        permission_rule=permission(company, "purchase_order"),
    )
    for tab in ("incoming_po", "outgoing_po"):
        add(f"{purchase_orders}.tabs.{tab}", FeatureType.TAB, parent=purchase_orders)
    for linked_object in ("documents", "structure"):
        add(
            f"{purchase_orders}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=purchase_orders,
        )

    billing = "company.financial.billing_management"
    add(
        billing,
        FeatureType.SUBMODULE,
        parent="company.financial",
        permission_rule=permission(company, "invoice"),
    )
    for tab in ("invoices", "credit_notes"):
        add(f"{billing}.tabs.{tab}", FeatureType.TAB, parent=billing)

    costs = "company.financial.costs_management"
    add(
        costs,
        FeatureType.SUBMODULE,
        parent="company.financial",
        permission_rules=(
            permission(company, "invoice"),
            permission(company, "expense_booking", "view", "review"),
        ),
    )
    for tab in ("supplier_invoices", "operating_costs"):
        add(
            f"{costs}.tabs.{tab}",
            FeatureType.TAB,
            parent=costs,
            permission_rule=permission(company, "invoice"),
        )
    add(
        f"{costs}.tabs.expense_reports",
        FeatureType.TAB,
        parent=costs,
        permission_rule=permission(company, "expense_booking", "view", "review"),
    )

    hr = "company.human_resources"
    add(hr, FeatureType.MODULE)
    hr_management = f"{hr}.hr_management"
    add(
        hr_management,
        FeatureType.SUBMODULE,
        parent=hr,
        permission_rules=(
            permission(company, "resources"),
            permission(company, "staff_management"),
        ),
    )
    add(
        f"{hr_management}.tabs.resource_allocations",
        FeatureType.TAB,
        parent=hr_management,
        permission_rule=permission(company, "resources"),
    )
    add(
        f"{hr_management}.tabs.staff_management",
        FeatureType.TAB,
        parent=hr_management,
        permission_rule=permission(company, "staff_management"),
    )
    time_booking = f"{hr}.time_booking"
    add(
        time_booking,
        FeatureType.SUBMODULE,
        parent=hr,
        permission_rules=(
            permission(company, "time_booking", "view", "review"),
            permission(company, "leave_request", "view", "review"),
        ),
    )
    add(
        f"{time_booking}.tabs.timesheets",
        FeatureType.TAB,
        parent=time_booking,
        permission_rule=permission(company, "time_booking", "view", "review"),
    )
    add(
        f"{time_booking}.tabs.leaves",
        FeatureType.TAB,
        parent=time_booking,
        permission_rule=permission(company, "leave_request", "view", "review"),
    )
    add(
        f"{hr}.overview",
        FeatureType.SUBMODULE,
        parent=hr,
        permission_rule=permission(company, "resources"),
    )
    talents = f"{hr}.talents_acquisition"
    add(
        talents,
        FeatureType.SUBMODULE,
        parent=hr,
        permission_rule=permission(company, "resources"),
    )
    for tab in ("list", "search", "creation"):
        add(f"{talents}.tabs.{tab}", FeatureType.TAB, parent=talents)
    trainings = f"{hr}.trainings"
    add(
        trainings,
        FeatureType.SUBMODULE,
        parent=hr,
        permission_rule=permission(company, "resources"),
    )
    add(f"{trainings}.tabs.list", FeatureType.TAB, parent=trainings)

    add(
        "company.feedback",
        FeatureType.MODULE,
        permission_rule=permission(company, "contact_management"),
    )
    add(
        "company.configuration",
        FeatureType.MODULE,
        permission_rule=permission(company, "company_configurations"),
    )
    add(
        "company.configuration.document_templates",
        FeatureType.SUBMODULE,
        parent="company.configuration",
        permission_rule=permission(company, "project_content"),
    )

    add("project", FeatureType.SECTION, solutions=PROJECT_SOLUTIONS)
    add(
        "project.dashboard",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "project"),
    )
    for tab in ("dashboard", "reports", "milestone_status"):
        add(
            f"project.dashboard.tabs.{tab}",
            FeatureType.TAB,
            parent="project.dashboard",
            solutions=PROJECT_SOLUTIONS,
        )

    add(
        "project.action_items",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "action_item"),
    )
    for tab in ("list", "board", "time", "calendar", "gantt"):
        add(
            f"project.action_items.tabs.{tab}",
            FeatureType.TAB,
            parent="project.action_items",
            solutions=PROJECT_SOLUTIONS,
        )
    for linked_object in (
        "comments",
        "documents",
        "structure",
        "predecessors",
        "dependents",
        "requirements",
    ):
        add(
            f"project.action_items.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent="project.action_items",
            solutions=PROJECT_SOLUTIONS,
            permission_rule=(
                permission(project, "requirements")
                if linked_object == "requirements"
                else None
            ),
        )

    add(
        "project.calendar",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "calendar_events"),
    )
    for linked_object in ("observations", "documents", "structure"):
        add(
            f"project.calendar.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent="project.calendar",
            solutions=PROJECT_SOLUTIONS,
        )

    add(
        "project.documents",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "documents"),
    )
    for tab in ("folder", "register"):
        add(
            f"project.documents.tabs.{tab}",
            FeatureType.TAB,
            parent="project.documents",
            solutions=PROJECT_SOLUTIONS,
        )
    add(
        "project.documents.generated_content",
        FeatureType.SUBMODULE,
        parent="project.documents",
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "project_content"),
    )

    requirements = "project.system_requirements"
    add(requirements, FeatureType.MODULE, solutions=PROJECT_SOLUTIONS)
    demands = f"{requirements}.customer_demands"
    add(
        demands,
        FeatureType.SUBMODULE,
        parent=requirements,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "solution_demands"),
    )
    for linked_object in (
        "comments",
        "observations",
        "documents",
        "structure",
        "requirements",
    ):
        add(
            f"{demands}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=demands,
            solutions=PROJECT_SOLUTIONS,
        )
    technical_requirements = f"{requirements}.technical_requirements"
    add(
        technical_requirements,
        FeatureType.SUBMODULE,
        parent=requirements,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "requirements"),
    )
    for linked_object in (
        "comments",
        "observations",
        "documents",
        "structure",
        "demands",
    ):
        add(
            f"{technical_requirements}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=technical_requirements,
            solutions=PROJECT_SOLUTIONS,
        )

    phases = "project.phases_milestones"
    add(
        phases,
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rules=(
            permission(project, "milestone_management"),
            permission(project, "phases_management"),
        ),
    )
    add(
        f"{phases}.tabs.phases",
        FeatureType.TAB,
        parent=phases,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "phases_management"),
    )
    for tab in ("milestones", "calendar"):
        add(
            f"{phases}.tabs.{tab}",
            FeatureType.TAB,
            parent=phases,
            solutions=PROJECT_SOLUTIONS,
            permission_rule=permission(project, "milestone_management"),
        )
    for linked_object in ("documents", "structure"):
        add(
            f"{phases}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=phases,
            solutions=PROJECT_SOLUTIONS,
        )

    project_products = "project.product_services"
    add(project_products, FeatureType.MODULE, solutions=PROJECT_SOLUTIONS)
    bom = f"{project_products}.bill_of_material"
    add(
        bom,
        FeatureType.SUBMODULE,
        parent=project_products,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "bill_of_material"),
    )
    for linked_object in (
        "comments",
        "observations",
        "documents",
        "structure",
        "requirements",
        "available_product",
    ):
        add(
            f"{bom}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=bom,
            solutions=PROJECT_SOLUTIONS,
        )

    project_assembly_catalog = f"{project_products}.assembly_catalog"
    add(
        project_assembly_catalog,
        FeatureType.SUBMODULE,
        parent=project_products,
        solutions=PROJECT_SOLUTIONS,
        permission_rules=(
            permission(project, "project_assembly_catalog"),
            permission(company, "aas_models"),
        ),
    )
    for tab in (
        "search",
        "list",
        "semantic",
        "knowledge_graph",
        "cad_model",
        "sysml_models",
        "aas_models",
    ):
        add(
            f"{project_assembly_catalog}.tabs.{tab}",
            FeatureType.TAB,
            parent=project_assembly_catalog,
            solutions=PROJECT_SOLUTIONS,
            permission_rule=permission(
                company if tab == "aas_models" else project,
                (
                    "aas_models"
                    if tab == "aas_models"
                    else "project_assembly_catalog"
                ),
            ),
        )
    for linked_object in (
        "comments",
        "observations",
        "documents",
        "structure",
        "requirements",
    ):
        add(
            f"{project_assembly_catalog}.tabs.list.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=f"{project_assembly_catalog}.tabs.list",
            solutions=PROJECT_SOLUTIONS,
        )

    project_services = f"{project_products}.services"
    add(
        project_services,
        FeatureType.SUBMODULE,
        parent=project_products,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "documents"),
    )
    for tab in ("list", "search", "knowledge_graph", "aas_models"):
        add(
            f"{project_services}.tabs.{tab}",
            FeatureType.TAB,
            parent=project_services,
            solutions=PROJECT_SOLUTIONS,
        )
    for module in ("system_control", "system_simulation"):
        add(
            f"{project_products}.{module}",
            FeatureType.SUBMODULE,
            parent=project_products,
            solutions=PROJECT_SOLUTIONS,
            permission_rule=permission(project, "documents"),
        )

    execution = "project.execution"
    add(
        execution,
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "project"),
    )
    for module in (
        "transport",
        "sourcing",
        "procurement",
        "manufacturing",
        "commissioning",
        "operations",
        "decommissioning",
    ):
        add(
            f"{execution}.{module}",
            FeatureType.SUBMODULE,
            parent=execution,
            solutions=PROJECT_SOLUTIONS,
            permission_rule=permission(
                project,
                "transports" if module == "transport" else "project",
            ),
        )

    transport = f"{execution}.transport"
    for linked_object in ("comments", "observations", "documents", "structure"):
        add(
            f"{transport}.linked.{linked_object}",
            FeatureType.LINKED_OBJECT,
            parent=transport,
            solutions=PROJECT_SOLUTIONS,
        )

    object_assessment = "project.object_assessment"
    add(
        object_assessment,
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "object_assessments"),
    )
    for tab in ("photos", "notes", "sketch", "audio", "documents"):
        add(
            f"{object_assessment}.tabs.{tab}",
            FeatureType.TAB,
            parent=object_assessment,
            solutions=PROJECT_SOLUTIONS,
        )

    add(
        "project.site_reporting",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "site_reporting"),
    )
    add(
        "project.funding",
        FeatureType.MODULE,
        solutions=ENERGY_ONLY,
        permission_rule=permission(project, "funding"),
    )
    add(
        "project.configuration",
        FeatureType.MODULE,
        solutions=PROJECT_SOLUTIONS,
        permission_rule=permission(project, "ecpmp_configurations"),
    )

    return tuple(features)


DISPLAY_FEATURES = _build_registry()
DISPLAY_FEATURE_BY_KEY = {feature.key: feature for feature in DISPLAY_FEATURES}


def normalize_solution_id(solution: SolutionId | str) -> SolutionId:
    if isinstance(solution, SolutionId):
        return solution

    try:
        return SolutionId(solution)
    except ValueError:
        try:
            return _BACKEND_SOLUTION_TITLES[solution]
        except KeyError as exc:
            raise ValueError(f"Unsupported solution: {solution}") from exc


def get_display_features_for_solution(
    solution: SolutionId | str,
) -> tuple[DisplayFeature, ...]:
    solution_id = normalize_solution_id(solution)
    return tuple(
        feature for feature in DISPLAY_FEATURES if solution_id in feature.available_in
    )


def get_display_feature(key: str) -> DisplayFeature:
    try:
        return DISPLAY_FEATURE_BY_KEY[key]
    except KeyError as exc:
        raise KeyError(f"Unknown display feature key: {key}") from exc


def _find_cycles(
    features_by_key: dict[str, DisplayFeature],
    relationships: Callable[[DisplayFeature], Iterable[str]],
) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str, path: tuple[str, ...]) -> None:
        if key in visiting:
            cycle_start = path.index(key)
            cycle = (*path[cycle_start:], key)
            errors.append(" -> ".join(cycle))
            return
        if key in visited:
            return

        visiting.add(key)
        for related_key in relationships(features_by_key[key]):
            if related_key in features_by_key:
                visit(related_key, (*path, key))
        visiting.remove(key)
        visited.add(key)

    for feature_key in features_by_key:
        visit(feature_key, ())
    return errors


def validate_feature_registry(features: Iterable[DisplayFeature]) -> None:
    feature_list = tuple(features)
    features_by_key: dict[str, DisplayFeature] = {}
    errors: list[str] = []
    known_permission_modules = set(
        ADMIN_SERVER_MODULES + SOLUTION_MODULES + PROJECT_MODULES
    )

    for feature in feature_list:
        if not feature.key or feature.key.strip() != feature.key:
            errors.append(f"Invalid feature key: {feature.key!r}")
        if feature.key in features_by_key:
            errors.append(f"Duplicate feature key: {feature.key}")
        features_by_key[feature.key] = feature
        if not feature.available_in:
            errors.append(f"Feature has no available solution: {feature.key}")
        for permission_rule in feature.permissions:
            if permission_rule.module not in known_permission_modules:
                errors.append(
                    f"Unknown permission module {permission_rule.module!r} "
                    f"for {feature.key}"
                )
            if not permission_rule.actions:
                errors.append(f"Permission has no actions for {feature.key}")

    for feature in feature_list:
        if feature.parent_key:
            parent = features_by_key.get(feature.parent_key)
            if not parent:
                errors.append(
                    f"Unknown parent {feature.parent_key!r} for {feature.key}"
                )
            elif not feature.available_in.issubset(parent.available_in):
                errors.append(
                    f"Child {feature.key} is available outside parent "
                    f"{feature.parent_key}"
                )
        for dependency_key in feature.dependencies:
            dependency = features_by_key.get(dependency_key)
            if not dependency:
                errors.append(
                    f"Unknown dependency {dependency_key!r} for {feature.key}"
                )
            elif not feature.available_in.issubset(dependency.available_in):
                errors.append(
                    f"Feature {feature.key} is available outside dependency "
                    f"{dependency_key}"
                )

    parent_cycles = _find_cycles(
        features_by_key,
        lambda feature: (feature.parent_key,) if feature.parent_key else (),
    )
    dependency_cycles = _find_cycles(
        features_by_key,
        lambda feature: feature.dependencies,
    )
    relationship_cycles = _find_cycles(
        features_by_key,
        lambda feature: (
            *((feature.parent_key,) if feature.parent_key else ()),
            *feature.dependencies,
        ),
    )
    errors.extend(f"Parent cycle: {cycle}" for cycle in parent_cycles)
    errors.extend(f"Dependency cycle: {cycle}" for cycle in dependency_cycles)
    errors.extend(
        f"Parent/dependency cycle: {cycle}" for cycle in relationship_cycles
    )

    if errors:
        raise DisplayFeatureRegistryError("\n".join(errors))


validate_feature_registry(DISPLAY_FEATURES)
