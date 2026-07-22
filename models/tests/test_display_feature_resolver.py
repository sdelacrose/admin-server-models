from unittest import TestCase

from models.display_feature_resolver import (
    DisplayFeatureOverrideError,
    VisibilityReason,
    get_effective_visibility_map,
    merge_display_override_changes,
    normalize_display_overrides,
    resolve_display_features,
    sanitize_stored_display_overrides,
)
from models.display_feature_registry import SolutionId


class DisplayFeatureResolverTests(TestCase):
    def test_defaults_are_visible_for_available_features(self):
        resolved = resolve_display_features(SolutionId.ENERGY_CONSULTANT)
        self.assertTrue(all(item.configured_visible for item in resolved))
        self.assertTrue(all(item.effective_visible for item in resolved))

    def test_parent_hides_descendants_without_changing_child_configuration(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {"company.action_items": False},
            )
        }
        child = resolved["company.action_items.tabs.board"]

        self.assertTrue(child.configured_visible)
        self.assertFalse(child.effective_visible)
        self.assertEqual(child.reason, VisibilityReason.PARENT_HIDDEN)
        self.assertEqual(child.blocked_by, "company.action_items")

    def test_section_hides_all_modules_without_changing_child_configuration(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {
                    "company": False,
                    "company.action_items.tabs.board": False,
                },
            )
        }

        module = resolved["company.action_items"]
        child = resolved["company.action_items.tabs.board"]
        self.assertFalse(module.effective_visible)
        self.assertEqual(module.reason, VisibilityReason.PARENT_HIDDEN)
        self.assertEqual(module.blocked_by, "company")
        self.assertFalse(child.configured_visible)

    def test_disabled_documents_hide_linked_documents_and_structure(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {"company.documents": False},
            )
        }

        for key in (
            "company.action_items.linked.documents",
            "company.action_items.linked.structure",
            "company.product_services.machines.linked.documents",
            "company.product_services.equipments.linked.structure",
            "company.product_services.solution_space.tabs.list.linked.documents",
        ):
            self.assertFalse(resolved[key].effective_visible)
            self.assertEqual(resolved[key].reason, VisibilityReason.DEPENDENCY_HIDDEN)
            self.assertEqual(resolved[key].blocked_by, "company.documents")

    def test_source_module_can_remain_visible_when_local_link_is_hidden(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {"company.action_items.linked.documents": False},
            )
        }

        self.assertTrue(resolved["company.documents"].effective_visible)
        linked_documents = resolved["company.action_items.linked.documents"]
        self.assertFalse(linked_documents.effective_visible)
        self.assertEqual(linked_documents.reason, VisibilityReason.SELF_HIDDEN)

    def test_disabled_project_documents_hide_transport_document_links(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {"project.documents": False},
            )
        }

        for key in (
            "project.execution.transport.linked.documents",
            "project.execution.transport.linked.structure",
        ):
            self.assertFalse(resolved[key].effective_visible)
            self.assertEqual(resolved[key].reason, VisibilityReason.DEPENDENCY_HIDDEN)
            self.assertEqual(resolved[key].blocked_by, "project.documents")

    def test_cross_module_dependencies_are_resolved(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                {"company.product_services.machines": False},
            )
        }
        linked_machines = resolved["company.projects.linked.machines"]

        self.assertFalse(linked_machines.effective_visible)
        self.assertEqual(linked_machines.reason, VisibilityReason.DEPENDENCY_HIDDEN)
        self.assertEqual(
            linked_machines.blocked_by,
            "company.product_services.machines",
        )

    def test_unavailable_features_are_filtered_by_default(self):
        enterprise = {
            item.key
            for item in resolve_display_features(SolutionId.ENTERPRISE)
        }
        core = {item.key for item in resolve_display_features(SolutionId.CORE)}

        self.assertNotIn("project.funding", enterprise)
        self.assertFalse(any(key.startswith("project.") for key in core))

    def test_unavailable_features_can_be_returned_with_reason(self):
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENTERPRISE,
                include_unavailable=True,
            )
        }
        funding = resolved["project.funding"]

        self.assertFalse(funding.effective_visible)
        self.assertEqual(
            funding.reason,
            VisibilityReason.NOT_AVAILABLE_FOR_SOLUTION,
        )

    def test_unknown_unavailable_and_non_boolean_overrides_are_rejected(self):
        cases = (
            {"company.unknown": False},
            {"project.funding": False},
            {"company.documents": "false"},
        )
        for overrides in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(DisplayFeatureOverrideError):
                    normalize_display_overrides(SolutionId.ENTERPRISE, overrides)

    def test_stale_stored_overrides_are_ignored_during_runtime_reads(self):
        sanitized = sanitize_stored_display_overrides(
            SolutionId.ENTERPRISE,
            {
                "company.unknown": False,
                "project.funding": False,
                "company.documents": "false",
                "company.action_items": False,
            },
        )

        self.assertEqual(sanitized, {"company.action_items": False})
        effective = get_effective_visibility_map(
            SolutionId.ENTERPRISE,
            {
                "company.unknown": False,
                "company.action_items": False,
            },
        )
        self.assertFalse(effective["company.action_items"])

    def test_default_values_are_removed_from_sparse_overrides(self):
        self.assertEqual(
            normalize_display_overrides(
                SolutionId.ENERGY_CONSULTANT,
                {
                    "company.documents": True,
                    "company.action_items": False,
                },
            ),
            {"company.action_items": False},
        )

    def test_override_changes_support_update_and_reset_to_default(self):
        current = {
            "company.documents": False,
            "company.action_items": False,
        }
        merged = merge_display_override_changes(
            SolutionId.ENERGY_CONSULTANT,
            current,
            {
                "company.documents": None,
                "company.action_items.tabs.board": False,
            },
        )

        self.assertEqual(
            merged,
            {
                "company.action_items": False,
                "company.action_items.tabs.board": False,
            },
        )

    def test_reenabling_parent_restores_preserved_child_setting(self):
        current = {
            "company.action_items": False,
            "company.action_items.tabs.board": False,
        }
        restored = merge_display_override_changes(
            SolutionId.ENERGY_CONSULTANT,
            current,
            {"company.action_items": None},
        )
        resolved = {
            item.key: item
            for item in resolve_display_features(
                SolutionId.ENERGY_CONSULTANT,
                restored,
            )
        }

        self.assertTrue(resolved["company.action_items"].effective_visible)
        self.assertFalse(
            resolved["company.action_items.tabs.board"].effective_visible
        )
        self.assertEqual(
            resolved["company.action_items.tabs.board"].reason,
            VisibilityReason.SELF_HIDDEN,
        )

    def test_effective_map_contains_only_available_features(self):
        effective = get_effective_visibility_map(SolutionId.CORE)
        self.assertTrue(effective)
        self.assertFalse(any(key.startswith("project.") for key in effective))
