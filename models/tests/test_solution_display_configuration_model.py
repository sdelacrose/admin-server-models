from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from models.display_feature_registry import DISPLAY_FEATURE_REGISTRY_VERSION
from models.models import CompanyProfile, SolutionDisplayConfiguration


class SolutionDisplayConfigurationModelTests(SimpleTestCase):
    def build_configuration(self, **overrides):
        values = {
            "company": CompanyProfile(),
            "solution": "energy_consultant_solution",
            "registry_version": DISPLAY_FEATURE_REGISTRY_VERSION,
            "overrides": {},
        }
        values.update(overrides)
        return SolutionDisplayConfiguration(**values)

    def test_clean_normalizes_solution_title_and_sparse_overrides(self):
        configuration = self.build_configuration(
            solution="Energy Consultant Solution",
            overrides={
                "company.documents": True,
                "company.action_items": False,
            },
        )

        configuration.clean()

        self.assertEqual(configuration.solution, "energy_consultant_solution")
        self.assertEqual(
            configuration.overrides,
            {"company.action_items": False},
        )

    def test_all_solutions_are_configurable_independent_of_licenses(self):
        self.assertEqual(
            {value for value, _label in SolutionDisplayConfiguration.SOLUTION_CHOICES},
            {
                "energy_consultant_solution",
                "enterprise_solution",
                "core_solution",
            },
        )

    def test_clean_rejects_feature_unavailable_for_solution(self):
        configuration = self.build_configuration(
            solution="enterprise_solution",
            overrides={"project.funding": False},
        )

        with self.assertRaises(ValidationError) as context:
            configuration.clean()

        self.assertIn("overrides", context.exception.message_dict)

    def test_clean_rejects_unsupported_solution(self):
        configuration = self.build_configuration(solution="unsupported")

        with self.assertRaises(ValidationError) as context:
            configuration.clean()

        self.assertIn("solution", context.exception.message_dict)

    def test_clean_rejects_non_positive_registry_version(self):
        configuration = self.build_configuration(registry_version=0)

        with self.assertRaises(ValidationError) as context:
            configuration.clean()

        self.assertIn("registry_version", context.exception.message_dict)
