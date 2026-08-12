from copy import deepcopy
from unittest import TestCase

from models.hierarchical_configurations import (
    AREA_OF_EXPERTISE_KEY,
    DOCUMENT_DISCIPLINES_KEY,
    HierarchicalConfigurationError,
    annotate_default_nodes,
    annotate_nested_configurations,
    flatten_nested_configuration,
    get_default_nested_configuration_values,
    get_default_nested_configuration,
    merge_nested_configurations,
    normalize_nested_configuration,
    prepare_nested_configurations_update,
    resolve_nested_configurations,
)


class HierarchicalConfigurationTests(TestCase):
    def test_default_document_disciplines_match_functional_specification(self):
        hierarchy = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        group_labels = [group["label"] for group in hierarchy["groups"]]
        children = [
            child
            for group in hierarchy["groups"]
            for child in group["children"]
        ]

        self.assertEqual(
            group_labels,
            [
                "Construction & Site Management",
                "Corporate Functions",
                "Digital & Information Management",
                "Engineering",
                "Finance & Business",
                "Operations & Maintenance",
                "Procurement & Contracts",
                "Project Management & Controls",
                "Quality, HSE & Compliance",
                "Supply Chain & Logistics",
                "Other",
            ],
        )
        self.assertEqual(len(children), 55)
        self.assertEqual(len({child["id"] for child in children}), len(children))
        self.assertEqual(len({child["code"] for child in children}), len(children))
        self.assertFalse(
            any(
                "translations" in node
                for group in hierarchy["groups"]
                for node in [group, *group["children"]]
            )
        )

    def test_default_area_of_expertise_matches_functional_specification(self):
        hierarchy = get_default_nested_configuration(AREA_OF_EXPERTISE_KEY)
        actual = {
            group["label"]: [child["label"] for child in group["children"]]
            for group in hierarchy["groups"]
        }

        self.assertEqual(
            actual,
            {
                "Project & Program Management": [
                    "Project Management",
                    "Program Management",
                    "Portfolio Management (PPM)",
                    "PMO",
                    "Planning & Scheduling",
                    "Cost Control / Cost Engineering",
                    "Risk Management",
                    "Change Control Management",
                    "Earned Value Management (EVM)",
                    "Stakeholder Management",
                    "Documentation Management",
                ],
                "Engineering & Technical Management": [
                    "Engineering Management",
                    "Systems Engineering",
                    "Requirements Management",
                    "Interface Management",
                    "Configuration Management",
                    "Design Coordination",
                    "Technical Documentation",
                    "Validation & Verification",
                ],
                "Construction & Site Management": [
                    "Construction Management",
                    "Site Management",
                    "Commissioning",
                    "Handover & Close-out",
                    "Field Engineering",
                    "Workface Planning",
                    "Authorities & Permits",
                ],
                "Procurement, Contracts & Claims": [
                    "Procurement",
                    "Supplier Management",
                    "Subcontract Management",
                    "Contract Management",
                    "Tendering / Bids Management",
                    "Contract Administration",
                    "Claims Management",
                ],
                "Quality, HSE & Compliance": [
                    "Quality Management (QA/QC)",
                    "Inspections",
                    "Audits",
                    "HSE Management",
                    "Safety",
                    "Regulatory Compliance",
                    "Sustainability",
                ],
                "Operations & Maintenance": [
                    "Operations Management",
                    "Maintenance Management",
                    "Asset Management",
                    "Reliability Engineering",
                    "Predictive Maintenance",
                ],
                "Manufacturing & Industrial Performance": [
                    "Production Management",
                    "Lean Manufacturing",
                    "Continuous Improvement",
                    "Six Sigma",
                    "Industrial Engineering",
                    "Performance Management (OEE)",
                ],
                "Supply Chain & Logistics": [
                    "Supply Chain Management",
                    "Logistics",
                    "Materials Management",
                    "Inventory Management",
                    "Warehousing",
                    "Transport & Customs",
                ],
                "Digital, Data & Project Tools": [
                    "Project Information Management",
                    "BIM Management",
                    "ERP / MES / CMMS",
                    "Data Analysis & BI",
                    "Digital Transformation",
                    "Workflow Automation",
                ],
                "Finance & Commercial Management": [
                    "Project Finance",
                    "Budgeting & Forecasting",
                    "CAPEX / OPEX Management",
                    "Business Case & ROI",
                    "Controlling",
                    "Commercial Management",
                ],
                "People, Organization & Change": [
                    "Organizational Design",
                    "Workforce Planning",
                    "Training & Competency",
                    "Organizational Change Management",
                    "Transformation Programs",
                    "Communication Management",
                ],
                "Industry / Sector Expertise": [
                    "Energy & Power",
                    "Renewables",
                    "Oil & Gas",
                    "Nuclear",
                    "Chemicals / Pharma",
                    "Automotive",
                    "Aerospace & Defense",
                    "Rail & Mobility",
                    "Marine / Offshore",
                    "Utilities",
                    "Data Centers",
                ],
            },
        )

    def test_normalization_discards_frontend_translation_metadata(self):
        normalized = normalize_nested_configuration(
            AREA_OF_EXPERTISE_KEY,
            {
                "groups": [
                    {
                        "id": "custom-group",
                        "label": "Custom Group",
                        "translations": {"fr": "Groupe personnalisé"},
                        "children": [
                            {
                                "id": "custom-child",
                                "label": "Custom Child",
                                "translations": {"fr": "Option personnalisée"},
                            }
                        ],
                    }
                ]
            },
            enforce_defaults=False,
        )

        self.assertEqual(
            normalized,
            {
                "groups": [
                    {
                        "id": "custom-group",
                        "label": "Custom Group",
                        "children": [
                            {"id": "custom-child", "label": "Custom Child"}
                        ],
                    }
                ]
            },
        )

    def test_default_hierarchies_are_valid(self):
        disciplines = normalize_nested_configuration(
            DOCUMENT_DISCIPLINES_KEY,
            get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY),
        )
        expertise = normalize_nested_configuration(
            AREA_OF_EXPERTISE_KEY,
            get_default_nested_configuration(AREA_OF_EXPERTISE_KEY),
        )

        self.assertEqual(disciplines["groups"][-1]["label"], "Other")
        operations = next(
            group
            for group in expertise["groups"]
            if group["label"] == "Operations & Maintenance"
        )
        self.assertEqual(
            [child["label"] for child in operations["children"]],
            [
                "Operations Management",
                "Maintenance Management",
                "Asset Management",
                "Reliability Engineering",
                "Predictive Maintenance",
            ],
        )

    def test_flatten_preserves_codes_for_document_disciplines(self):
        flattened = flatten_nested_configuration(
            DOCUMENT_DISCIPLINES_KEY,
            get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY),
        )

        self.assertIn("Electrical Engineering:ELE", flattened)
        self.assertIn("Civil Engineering:CIV", flattened)
        self.assertIn("Structural Engineering:STR", flattened)

    def test_default_nodes_cannot_be_removed_or_edited(self):
        missing_group = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        missing_group["groups"] = missing_group["groups"][1:]
        with self.assertRaisesRegex(
            HierarchicalConfigurationError,
            "Default group cannot be removed",
        ):
            normalize_nested_configuration(DOCUMENT_DISCIPLINES_KEY, missing_group)

        renamed_child = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        renamed_child["groups"][0]["children"][0]["label"] = "Renamed"
        with self.assertRaisesRegex(
            HierarchicalConfigurationError,
            "Default child cannot be edited",
        ):
            normalize_nested_configuration(DOCUMENT_DISCIPLINES_KEY, renamed_child)

    def test_default_groups_and_children_can_be_reordered(self):
        reordered = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        reordered["groups"].reverse()
        reordered["groups"][-1]["children"].reverse()

        normalized = normalize_nested_configuration(
            DOCUMENT_DISCIPLINES_KEY,
            reordered,
        )

        self.assertEqual(normalized["groups"][0]["label"], "Other")

    def test_custom_child_can_be_added_but_not_moved_between_groups(self):
        existing = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        existing["groups"][0]["children"].append(
            {"id": "custom-planning", "label": "Custom Planning", "code": "CPL"}
        )
        normalized = normalize_nested_configuration(
            DOCUMENT_DISCIPLINES_KEY,
            existing,
        )

        moved = deepcopy(normalized)
        custom = moved["groups"][0]["children"].pop()
        moved["groups"][1]["children"].append(custom)
        with self.assertRaisesRegex(
            HierarchicalConfigurationError,
            "Child cannot be moved to another group",
        ):
            normalize_nested_configuration(
                DOCUMENT_DISCIPLINES_KEY,
                moved,
                existing_configuration=normalized,
            )

    def test_duplicate_labels_and_codes_are_rejected(self):
        hierarchy = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        hierarchy["groups"][-1]["children"].append(
            {"id": "duplicate-code", "label": "Custom Discipline", "code": "ELE"}
        )
        with self.assertRaisesRegex(
            HierarchicalConfigurationError,
            "Duplicate child code",
        ):
            normalize_nested_configuration(DOCUMENT_DISCIPLINES_KEY, hierarchy)

    def test_merge_updates_one_key_without_removing_another(self):
        current = {
            DOCUMENT_DISCIPLINES_KEY: get_default_nested_configuration(
                DOCUMENT_DISCIPLINES_KEY
            ),
            AREA_OF_EXPERTISE_KEY: get_default_nested_configuration(
                AREA_OF_EXPERTISE_KEY
            ),
        }
        disciplines = deepcopy(current[DOCUMENT_DISCIPLINES_KEY])
        disciplines["groups"][-1]["children"].append(
            {"id": "custom-other", "label": "Custom Other", "code": "CUS"}
        )

        merged = merge_nested_configurations(
            current,
            {DOCUMENT_DISCIPLINES_KEY: disciplines},
        )

        self.assertEqual(
            merged[AREA_OF_EXPERTISE_KEY],
            current[AREA_OF_EXPERTISE_KEY],
        )

    def test_default_metadata_is_derived(self):
        annotated = annotate_default_nodes(
            AREA_OF_EXPERTISE_KEY,
            get_default_nested_configuration(AREA_OF_EXPERTISE_KEY),
        )

        self.assertTrue(annotated["groups"][0]["is_default"])
        self.assertTrue(annotated["groups"][0]["children"][0]["is_default"])

    def test_blank_storage_resolves_to_complete_defaults(self):
        resolved = resolve_nested_configurations({})

        self.assertIn(DOCUMENT_DISCIPLINES_KEY, resolved)
        self.assertIn(AREA_OF_EXPERTISE_KEY, resolved)

    def test_update_regenerates_compatibility_values(self):
        disciplines = get_default_nested_configuration(DOCUMENT_DISCIPLINES_KEY)
        disciplines["groups"][-1]["children"].append(
            {"id": "custom-test", "label": "Custom Test", "code": "CTE"}
        )

        merged, flattened = prepare_nested_configurations_update(
            {},
            {DOCUMENT_DISCIPLINES_KEY: disciplines},
        )

        self.assertIn(AREA_OF_EXPERTISE_KEY, merged)
        self.assertIn("Custom Test:CTE", flattened[DOCUMENT_DISCIPLINES_KEY])

    def test_complete_annotation_preserves_flattened_defaults(self):
        nested, flattened = get_default_nested_configuration_values()
        annotated = annotate_nested_configurations(nested)

        self.assertTrue(
            annotated[DOCUMENT_DISCIPLINES_KEY]["groups"][0]["is_default"]
        )
        self.assertIn("Electrical Engineering:ELE", flattened[DOCUMENT_DISCIPLINES_KEY])
