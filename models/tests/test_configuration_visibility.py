from django.test import SimpleTestCase

from models.configuration_visibility import (
    ConfigurationVisibilityError,
    annotate_flat_values,
    annotate_nested_visibility,
    clean_configuration_visibility,
    filter_enabled_flat_values,
    filter_enabled_nested_configurations,
    prepare_configuration_visibility_update,
)
from models.hierarchical_configurations import (
    AREA_OF_EXPERTISE_KEY,
    get_default_nested_configuration,
)


class ConfigurationVisibilityTests(SimpleTestCase):
    def setUp(self):
        self.area = get_default_nested_configuration(AREA_OF_EXPERTISE_KEY)
        self.values = {
            "contract_type": ["Fixed Price", "Time and Materials"],
            "international_standard": ["DIN"],
            "major_project_model": ["EPC"],
            "commercial_model": ["Fixed Price Model"],
            "supporting_agreement": ["Framework Agreement"],
        }
        self.nested = {AREA_OF_EXPERTISE_KEY: self.area}

    def test_empty_visibility_keeps_every_flat_value_enabled(self):
        self.assertEqual(
            filter_enabled_flat_values(
                self.values["contract_type"],
                {},
                "contract_type",
            ),
            self.values["contract_type"],
        )

    def test_flat_visibility_is_annotated_and_filtered(self):
        visibility = {
            "contract_type": {"disabled_values": ["Time and Materials"]}
        }

        self.assertEqual(
            annotate_flat_values(
                self.values["contract_type"],
                ["Fixed Price"],
                visibility,
                "contract_type",
            ),
            [
                {
                    "value": "Fixed Price",
                    "is_default": True,
                    "is_enabled": True,
                },
                {
                    "value": "Time and Materials",
                    "is_default": False,
                    "is_enabled": False,
                },
            ],
        )
        self.assertEqual(
            filter_enabled_flat_values(
                self.values["contract_type"],
                visibility,
                "contract_type",
            ),
            ["Fixed Price"],
        )

    def test_nested_group_and_child_states_are_independent(self):
        first_group = self.area["groups"][0]
        first_child = first_group["children"][0]
        visibility = {
            AREA_OF_EXPERTISE_KEY: {
                "disabled_group_ids": [first_group["id"]],
                "disabled_child_ids": [first_child["id"]],
            }
        }

        annotated = annotate_nested_visibility(self.nested, visibility)
        self.assertFalse(
            annotated[AREA_OF_EXPERTISE_KEY]["groups"][0]["is_enabled"]
        )
        self.assertFalse(
            annotated[AREA_OF_EXPERTISE_KEY]["groups"][0]["children"][0][
                "is_enabled"
            ]
        )

        filtered = filter_enabled_nested_configurations(self.nested, visibility)
        filtered_group_ids = {
            group["id"]
            for group in filtered[AREA_OF_EXPERTISE_KEY]["groups"]
        }
        self.assertNotIn(first_group["id"], filtered_group_ids)

    def test_update_rejects_unknown_disabled_values(self):
        with self.assertRaises(ConfigurationVisibilityError):
            prepare_configuration_visibility_update(
                {},
                {"contract_type": {"disabled_values": ["Unknown"]}},
                configured_values=self.values,
                nested_configurations=self.nested,
            )

    def test_cleanup_removes_deleted_flat_and_nested_options(self):
        visibility = {
            "contract_type": {
                "disabled_values": ["Fixed Price", "Deleted Type"]
            },
            AREA_OF_EXPERTISE_KEY: {
                "disabled_group_ids": [
                    self.area["groups"][0]["id"],
                    "deleted-group",
                ],
                "disabled_child_ids": ["deleted-child"],
            },
        }

        cleaned = clean_configuration_visibility(
            visibility,
            configured_values=self.values,
            nested_configurations=self.nested,
        )

        self.assertEqual(
            cleaned["contract_type"]["disabled_values"],
            ["Fixed Price"],
        )
        self.assertEqual(
            cleaned[AREA_OF_EXPERTISE_KEY]["disabled_group_ids"],
            [self.area["groups"][0]["id"]],
        )
        self.assertNotIn(
            "disabled_child_ids",
            cleaned[AREA_OF_EXPERTISE_KEY],
        )
