from dataclasses import replace
from unittest import TestCase

from models.display_feature_registry import (
    ALL_SOLUTIONS,
    DISPLAY_FEATURE_BY_KEY,
    DISPLAY_FEATURE_REGISTRY_REVISION,
    DISPLAY_FEATURE_REGISTRY_VERSION,
    DISPLAY_FEATURE_SCHEMA_MAJOR,
    DISPLAY_FEATURES,
    DisplayFeature,
    DisplayFeatureRegistryError,
    FeatureType,
    PermissionScope,
    SolutionId,
    get_display_features_for_solution,
    normalize_solution_id,
    validate_feature_registry,
)


class DisplayFeatureRegistryTests(TestCase):
    def setUp(self):
        self.energy_keys = {
            feature.key
            for feature in get_display_features_for_solution(
                SolutionId.ENERGY_CONSULTANT
            )
        }
        self.enterprise_keys = {
            feature.key
            for feature in get_display_features_for_solution(SolutionId.ENTERPRISE)
        }
        self.core_keys = {
            feature.key
            for feature in get_display_features_for_solution(SolutionId.CORE)
        }

    def test_canonical_registry_is_valid(self):
        validate_feature_registry(DISPLAY_FEATURES)
        self.assertEqual(len(DISPLAY_FEATURES), len(DISPLAY_FEATURE_BY_KEY))
        self.assertEqual(DISPLAY_FEATURE_SCHEMA_MAJOR, 1)
        self.assertEqual(DISPLAY_FEATURE_REGISTRY_REVISION, 4)
        self.assertEqual(DISPLAY_FEATURE_REGISTRY_VERSION, 4)

    def test_solution_catalogs_match_solution_profiles(self):
        all_keys = {feature.key for feature in DISPLAY_FEATURES}
        company_keys = {
            key
            for key in all_keys
            if key == "company" or key.startswith("company.")
        }

        self.assertEqual(len(self.energy_keys), 187)
        self.assertEqual(len(self.enterprise_keys), 186)
        self.assertEqual(len(self.core_keys), 99)
        self.assertEqual(self.energy_keys, all_keys)
        self.assertEqual(
            self.energy_keys - self.enterprise_keys,
            {"project.funding"},
        )
        self.assertEqual(self.core_keys, company_keys)
        self.assertNotIn("project", self.core_keys)
        self.assertFalse(any(key.startswith("project.") for key in self.core_keys))

    def test_company_and_project_sections_own_root_modules(self):
        self.assertEqual(
            DISPLAY_FEATURE_BY_KEY["company.dashboard"].parent_key,
            "company",
        )
        self.assertEqual(
            DISPLAY_FEATURE_BY_KEY["project.dashboard"].parent_key,
            "project",
        )

    def test_company_dashboard_is_available_without_module_permission(self):
        self.assertEqual(
            DISPLAY_FEATURE_BY_KEY["company.dashboard"].permissions,
            (),
        )

    def test_all_three_solutions_are_always_supported(self):
        self.assertEqual(
            {solution.value for solution in SolutionId},
            {
                "energy_consultant_solution",
                "enterprise_solution",
                "core_solution",
            },
        )

    def test_solution_titles_and_ids_are_normalized(self):
        self.assertEqual(
            normalize_solution_id("Energy Consultant Solution"),
            SolutionId.ENERGY_CONSULTANT,
        )
        self.assertEqual(
            normalize_solution_id("enterprise_solution"),
            SolutionId.ENTERPRISE,
        )
        with self.assertRaises(ValueError):
            normalize_solution_id("unknown_solution")

    def test_confirmed_dashboard_and_action_item_tabs(self):
        expected_company_tabs = {
            "company.dashboard.tabs.global_dashboard",
            "company.dashboard.tabs.personal_dashboard",
            "company.dashboard.tabs.reports",
        }
        expected_project_tabs = {
            "project.dashboard.tabs.dashboard",
            "project.dashboard.tabs.reports",
            "project.dashboard.tabs.milestone_status",
        }

        self.assertTrue(expected_company_tabs.issubset(self.energy_keys))
        self.assertTrue(expected_project_tabs.issubset(self.energy_keys))
        self.assertNotIn("company.action_items.tabs.gantt", self.energy_keys)
        self.assertNotIn("project.action_items.tabs.gantt", self.energy_keys)

    def test_confirmed_linked_features_are_registered(self):
        expected_keys = {
            "company.product_services.machines.linked.comments",
            "company.product_services.machines.linked.projects",
            "company.product_services.machines.linked.documents",
            "company.product_services.machines.linked.structure",
            "company.product_services.equipments.linked.comments",
            "company.product_services.equipments.linked.documents",
            "company.product_services.equipments.linked.structure",
            "company.projects.linked.machines",
            "company.product_services.solution_space.tabs.list.linked.comments",
            "company.product_services.solution_space.tabs.list.linked.documents",
            "company.product_services.solution_space.tabs.list.linked.structure",
            "project.product_services.solution_space.tabs.list.linked.comments",
            "project.product_services.solution_space.tabs.list.linked.observations",
            "project.product_services.solution_space.tabs.list.linked.documents",
            "project.product_services.solution_space.tabs.list.linked.structure",
            "project.product_services.solution_space.tabs.list.linked.requirements",
            "project.execution.transport.linked.comments",
            "project.execution.transport.linked.observations",
            "project.execution.transport.linked.documents",
            "project.execution.transport.linked.structure",
        }
        self.assertTrue(expected_keys.issubset(self.energy_keys))

    def test_linked_features_reference_source_module_dependencies(self):
        expected_dependencies = {
            "company.action_items.linked.documents": ("company.documents",),
            "company.action_items.linked.structure": ("company.documents",),
            "company.action_items.linked.opportunities": (
                "company.opportunities_offers",
            ),
            "company.product_services.machines.linked.projects": (
                "company.projects",
            ),
            "company.projects.linked.machines": (
                "company.product_services.machines",
            ),
            "project.calendar.linked.observations": (
                "project.object_assessment",
            ),
            "project.execution.transport.linked.observations": (
                "project.object_assessment",
            ),
            "project.execution.transport.linked.documents": (
                "project.documents",
            ),
            "project.execution.transport.linked.structure": (
                "project.documents",
            ),
            "project.product_services.bill_of_material.linked.available_product": (
                "company.product_services.available_products",
            ),
            "project.system_requirements.customer_demands.linked.requirements": (
                "project.system_requirements.technical_requirements",
            ),
            "project.system_requirements.technical_requirements.linked.demands": (
                "project.system_requirements.customer_demands",
            ),
        }

        for key, dependencies in expected_dependencies.items():
            self.assertEqual(DISPLAY_FEATURE_BY_KEY[key].dependencies, dependencies)

    def test_review_permissions_use_any_matching_action(self):
        for key in (
            "company.human_resources.time_booking",
            "company.human_resources.time_booking.tabs.timesheets",
            "company.human_resources.time_booking.tabs.leaves",
            "company.financial.costs_management.tabs.expense_reports",
        ):
            permission = DISPLAY_FEATURE_BY_KEY[key].permission
            self.assertIsNotNone(permission)
            self.assertEqual(permission.scope, PermissionScope.COMPANY)
            self.assertEqual(permission.actions, ("view", "review"))
            self.assertFalse(permission.require_all)

    def test_parent_features_preserve_alternative_permission_modules(self):
        expected_modules = {
            "company.financial.costs_management": {
                "invoice",
                "expense_booking",
            },
            "company.human_resources.hr_management": {
                "resources",
                "staff_management",
            },
            "company.human_resources.time_booking": {
                "time_booking",
                "leave_request",
            },
            "project.phases_milestones": {
                "milestone_management",
                "phases_management",
            },
        }

        for key, modules in expected_modules.items():
            self.assertEqual(
                {rule.module for rule in DISPLAY_FEATURE_BY_KEY[key].permissions},
                modules,
            )

    def test_duplicate_keys_are_rejected(self):
        duplicate = replace(DISPLAY_FEATURES[0])
        with self.assertRaisesRegex(DisplayFeatureRegistryError, "Duplicate"):
            validate_feature_registry((*DISPLAY_FEATURES, duplicate))

    def test_unknown_parent_is_rejected(self):
        invalid = DisplayFeature(
            key="company.invalid",
            feature_type=FeatureType.TAB,
            label_key="DisplayConfiguration.Features.company.invalid",
            available_in=ALL_SOLUTIONS,
            parent_key="company.missing",
        )
        with self.assertRaisesRegex(DisplayFeatureRegistryError, "Unknown parent"):
            validate_feature_registry((*DISPLAY_FEATURES, invalid))

    def test_unknown_dependency_is_rejected(self):
        invalid = DisplayFeature(
            key="company.invalid_dependency",
            feature_type=FeatureType.LINKED_OBJECT,
            label_key="DisplayConfiguration.Features.company.invalid_dependency",
            available_in=ALL_SOLUTIONS,
            dependencies=("company.missing",),
        )
        with self.assertRaisesRegex(
            DisplayFeatureRegistryError,
            "Unknown dependency",
        ):
            validate_feature_registry((*DISPLAY_FEATURES, invalid))

    def test_parent_cycles_are_rejected(self):
        first = DisplayFeature(
            key="cycle.first",
            feature_type=FeatureType.MODULE,
            label_key="cycle.first",
            available_in=ALL_SOLUTIONS,
            parent_key="cycle.second",
        )
        second = DisplayFeature(
            key="cycle.second",
            feature_type=FeatureType.MODULE,
            label_key="cycle.second",
            available_in=ALL_SOLUTIONS,
            parent_key="cycle.first",
        )
        with self.assertRaisesRegex(DisplayFeatureRegistryError, "Parent cycle"):
            validate_feature_registry((first, second))

    def test_dependency_cycles_are_rejected(self):
        first = DisplayFeature(
            key="cycle.first",
            feature_type=FeatureType.MODULE,
            label_key="cycle.first",
            available_in=ALL_SOLUTIONS,
            dependencies=("cycle.second",),
        )
        second = DisplayFeature(
            key="cycle.second",
            feature_type=FeatureType.MODULE,
            label_key="cycle.second",
            available_in=ALL_SOLUTIONS,
            dependencies=("cycle.first",),
        )
        with self.assertRaisesRegex(DisplayFeatureRegistryError, "Dependency cycle"):
            validate_feature_registry((first, second))

    def test_combined_parent_dependency_cycles_are_rejected(self):
        first = DisplayFeature(
            key="cycle.first",
            feature_type=FeatureType.MODULE,
            label_key="cycle.first",
            available_in=ALL_SOLUTIONS,
            parent_key="cycle.second",
        )
        second = DisplayFeature(
            key="cycle.second",
            feature_type=FeatureType.MODULE,
            label_key="cycle.second",
            available_in=ALL_SOLUTIONS,
            dependencies=("cycle.first",),
        )
        with self.assertRaisesRegex(
            DisplayFeatureRegistryError,
            "Parent/dependency cycle",
        ):
            validate_feature_registry((first, second))
