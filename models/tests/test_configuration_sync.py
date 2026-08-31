from types import SimpleNamespace

from django.test import SimpleTestCase

from models import constants
from models.configuration_sync import (
    PRESERVE_LOCAL,
    ConfigurationSyncError,
    configuration_values_from_instance,
    merge_list_values,
    preserve_local_configuration,
    replace_configuration,
    validate_sync_strategy,
)
from models.configuration_templates import (
    CODED_FIELD_KIND,
    COMPANY_CONFIGURATION_FIELDS,
    PLAIN_FIELD_KIND,
    STATUS_FIELD_KIND,
    get_project_template_defaults,
)
from models.hierarchical_configurations import (
    AREA_OF_EXPERTISE_KEY,
    get_default_nested_configurations,
)
from models.models import ProjectConfigTemplate


class ConfigurationSyncTests(SimpleTestCase):
    def test_strategy_validation_rejects_unknown_values(self):
        self.assertEqual(validate_sync_strategy(PRESERVE_LOCAL), PRESERVE_LOCAL)
        with self.assertRaises(ConfigurationSyncError):
            validate_sync_strategy("unknown")

    def test_list_merge_rejects_malformed_configuration_values(self):
        with self.assertRaisesRegex(ConfigurationSyncError, "must be a list"):
            merge_list_values(
                "Local",
                ["Template"],
                field_kind=PLAIN_FIELD_KIND,
            )

    def test_plain_merge_preserves_local_order_and_matches_case_insensitively(self):
        merged = merge_list_values(
            ["Local", "Shared"],
            ["shared", "Admin"],
            field_kind=PLAIN_FIELD_KIND,
        )

        self.assertEqual(merged, ["Local", "Shared", "Admin"])

    def test_coded_and_status_merges_use_stable_identifiers(self):
        self.assertEqual(
            merge_list_values(
                ["Local label:ABC"],
                ["Template label:abc", "New value:XYZ"],
                field_kind=CODED_FIELD_KIND,
            ),
            ["Local label:ABC", "New value:XYZ"],
        )
        self.assertEqual(
            merge_list_values(
                ["Open:#111111"],
                ["open:#222222", "Closed:#333333"],
                field_kind=STATUS_FIELD_KIND,
            ),
            ["Open:#111111", "Closed:#333333"],
        )

    def test_preserve_merge_keeps_local_nested_values_and_appends_template_nodes(self):
        local_nested = get_default_nested_configurations()
        template_nested = get_default_nested_configurations()
        local_nested[AREA_OF_EXPERTISE_KEY]["groups"].append(
            {
                "id": "custom-shared-group",
                "label": "Local Group",
                "children": [
                    {"id": "custom-shared-child", "label": "Local Child"}
                ],
            }
        )
        template_nested[AREA_OF_EXPERTISE_KEY]["groups"].extend(
            [
                {
                    "id": "custom-shared-group",
                    "label": "Template Group",
                    "children": [
                        {
                            "id": "custom-shared-child",
                            "label": "Template Child",
                        },
                        {"id": "custom-new-child", "label": "New Child"},
                    ],
                },
                {
                    "id": "custom-new-group",
                    "label": "New Group",
                    "children": [],
                },
            ]
        )

        merged = preserve_local_configuration(
            {
                "contract_type": ["Local", "Shared"],
                "nested_configurations": local_nested,
                "configuration_visibility": {
                    "contract_type": {"disabled_values": ["Shared"]},
                    AREA_OF_EXPERTISE_KEY: {
                        "disabled_child_ids": ["custom-shared-child"]
                    },
                },
            },
            {
                "contract_type": ["Shared", "Admin"],
                "nested_configurations": template_nested,
                "configuration_visibility": {
                    "contract_type": {
                        "disabled_values": ["Shared", "Admin"]
                    },
                    AREA_OF_EXPERTISE_KEY: {
                        "disabled_group_ids": [
                            "custom-shared-group",
                            "custom-new-group",
                        ],
                        "disabled_child_ids": [
                            "custom-shared-child",
                            "custom-new-child",
                        ],
                    },
                },
            },
            field_names=COMPANY_CONFIGURATION_FIELDS,
        )

        self.assertEqual(merged["contract_type"], ["Local", "Shared", "Admin"])
        self.assertEqual(
            merged["configuration_visibility"]["contract_type"][
                "disabled_values"
            ],
            ["Shared", "Admin"],
        )
        groups = {
            group["id"]: group
            for group in merged["nested_configurations"][
                AREA_OF_EXPERTISE_KEY
            ]["groups"]
        }
        self.assertEqual(groups["custom-shared-group"]["label"], "Local Group")
        self.assertEqual(
            [
                child["label"]
                for child in groups["custom-shared-group"]["children"]
            ],
            ["Local Child", "New Child"],
        )
        nested_visibility = merged["configuration_visibility"][
            AREA_OF_EXPERTISE_KEY
        ]
        self.assertEqual(
            nested_visibility["disabled_group_ids"],
            ["custom-new-group"],
        )
        self.assertEqual(
            nested_visibility["disabled_child_ids"],
            ["custom-shared-child", "custom-new-child"],
        )

    def test_replace_returns_an_independent_template_copy(self):
        template = {"contract_type": ["Admin"]}

        replaced = replace_configuration(
            template,
            field_names=("contract_type",),
        )
        replaced["contract_type"].append("Changed")

        self.assertEqual(template["contract_type"], ["Admin"])

    def test_project_merge_does_not_emit_company_visibility(self):
        merged = preserve_local_configuration(
            {"labels": ["Local"]},
            {"labels": ["Admin"]},
        )

        self.assertEqual(merged["labels"], ["Local", "Admin"])
        self.assertNotIn("configuration_visibility", merged)

    def test_instance_values_returns_independent_registered_fields(self):
        instance = SimpleNamespace(contract_type=["Local"], ignored=["Ignored"])

        values = configuration_values_from_instance(
            instance,
            ("contract_type",),
        )
        values["contract_type"].append("Changed")

        self.assertEqual(instance.contract_type, ["Local"])

    def test_project_defaults_seed_overlap_without_replacing_project_document_types(self):
        source = SimpleNamespace(
            labels=["Admin Label"],
            document_types=["Company document type:CDT"],
            nested_configurations=get_default_nested_configurations(),
        )

        defaults = get_project_template_defaults(source)

        self.assertEqual(defaults["labels"], ["Admin Label"])
        self.assertNotIn("contract_type", defaults)
        self.assertEqual(defaults["document_types"], constants.GC_PROJECT_DOCUMENT_TYPES)

    def test_project_template_requires_exactly_one_owner(self):
        constraint_names = {
            constraint.name for constraint in ProjectConfigTemplate._meta.constraints
        }

        self.assertIn("project_config_template_single_owner", constraint_names)
