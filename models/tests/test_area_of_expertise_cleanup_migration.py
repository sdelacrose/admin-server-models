from importlib import import_module
from unittest import TestCase

from models.hierarchical_configurations import (
    AREA_OF_EXPERTISE_KEY,
    get_default_nested_configuration,
)


cleanup_migration = import_module(
    "models.migrations.0125_area_of_expertise_profile_fields"
)


class AreaOfExpertiseCleanupMigrationTests(TestCase):
    def test_cleanup_removes_custom_nodes_and_preserves_default_visibility(self):
        default = get_default_nested_configuration(AREA_OF_EXPERTISE_KEY)
        custom_area = get_default_nested_configuration(AREA_OF_EXPERTISE_KEY)
        custom_area["groups"].append(
            {
                "id": "custom-group",
                "label": "Custom Group",
                "children": [{"id": "custom-child", "label": "Custom Child"}],
            }
        )
        default_group_id = default["groups"][0]["id"]
        default_child_id = default["groups"][0]["children"][0]["id"]

        nested, visibility = cleanup_migration._clean_area_of_expertise(
            {
                AREA_OF_EXPERTISE_KEY: custom_area,
                "future_configuration": {"value": True},
            },
            {
                AREA_OF_EXPERTISE_KEY: {
                    "disabled_group_ids": [default_group_id, "custom-group"],
                    "disabled_child_ids": [default_child_id, "custom-child"],
                },
                "contract_type": {"disabled_values": ["Custom"]},
            },
            default,
        )

        self.assertEqual(nested[AREA_OF_EXPERTISE_KEY], default)
        self.assertEqual(nested["future_configuration"], {"value": True})
        self.assertEqual(
            visibility[AREA_OF_EXPERTISE_KEY],
            {
                "disabled_group_ids": [default_group_id],
                "disabled_child_ids": [default_child_id],
            },
        )
        self.assertEqual(
            visibility["contract_type"],
            {"disabled_values": ["Custom"]},
        )

    def test_cleanup_removes_empty_area_visibility(self):
        default = get_default_nested_configuration(AREA_OF_EXPERTISE_KEY)

        _, visibility = cleanup_migration._clean_area_of_expertise(
            {},
            {
                AREA_OF_EXPERTISE_KEY: {
                    "disabled_group_ids": ["custom-group"],
                    "disabled_child_ids": ["custom-child"],
                }
            },
            default,
        )

        self.assertNotIn(AREA_OF_EXPERTISE_KEY, visibility)
