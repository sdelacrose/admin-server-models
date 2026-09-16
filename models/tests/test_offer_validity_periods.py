from django.test import SimpleTestCase

from models.configuration_templates import (
    COMPANY_CONFIGURATION_FIELDS,
    get_company_configuration_defaults,
)
from models.configuration_sync import preserve_local_configuration
from models.models import CompanyConfig, GlobalConfig
from models.offer_validity_periods import (
    OfferValidityPeriodError,
    normalize_offer_validity_period,
    normalize_offer_validity_periods,
    parse_offer_validity_period,
)


class OfferValidityPeriodTests(SimpleTestCase):
    def test_parse_returns_duration_and_singular_unit(self):
        period = parse_offer_validity_period(" 15 : DAYS ")

        self.assertEqual(period.duration, 15)
        self.assertEqual(period.unit, "day")
        self.assertEqual(period.canonical_value, "15:day")

    def test_normalize_accepts_colon_or_whitespace_separator(self):
        self.assertEqual(normalize_offer_validity_period("1:months"), "1:month")
        self.assertEqual(normalize_offer_validity_period("6 Weeks"), "6:week")

    def test_normalize_list_preserves_order(self):
        self.assertEqual(
            normalize_offer_validity_periods(
                ["15 days", "1:month", "6 WEEKS", "1 year"]
            ),
            ["15:day", "1:month", "6:week", "1:year"],
        )

    def test_normalize_list_rejects_duplicate_canonical_values(self):
        with self.assertRaisesRegex(
            OfferValidityPeriodError,
            "Duplicate Offer validity period: 1:month",
        ):
            normalize_offer_validity_periods(["1 month", "1:months"])

    def test_normalize_list_allows_equivalent_distinct_units(self):
        self.assertEqual(
            normalize_offer_validity_periods(["7:day", "1:week"]),
            ["7:day", "1:week"],
        )

    def test_rejects_non_list_collections(self):
        with self.assertRaisesRegex(
            OfferValidityPeriodError,
            "must be a list",
        ):
            normalize_offer_validity_periods("1:month")

    def test_rejects_invalid_duration(self):
        for value in ("0:day", "1000:year", "1.5:month", "-1:week"):
            with self.subTest(value=value):
                with self.assertRaises(OfferValidityPeriodError):
                    normalize_offer_validity_period(value)

    def test_rejects_invalid_unit_or_format(self):
        for value in ("1:hour", "month", "1-month", ""):
            with self.subTest(value=value):
                with self.assertRaises(OfferValidityPeriodError):
                    normalize_offer_validity_period(value)

    def test_company_registry_and_defaults_include_empty_validity_periods(self):
        defaults = get_company_configuration_defaults()

        self.assertIn("offer_validity_periods", COMPANY_CONFIGURATION_FIELDS)
        self.assertEqual(defaults["offer_validity_periods"], [])

    def test_preserve_sync_keeps_local_order_and_appends_admin_periods(self):
        merged = preserve_local_configuration(
            {"offer_validity_periods": ["1:month", "15:day"]},
            {"offer_validity_periods": ["1:month", "6:week"]},
            field_names=("offer_validity_periods",),
        )

        self.assertEqual(
            merged["offer_validity_periods"],
            ["1:month", "15:day", "6:week"],
        )

    def test_shared_models_use_bounded_empty_array_fields(self):
        for model in (GlobalConfig, CompanyConfig):
            with self.subTest(model=model.__name__):
                field = model._meta.get_field("offer_validity_periods")

                self.assertEqual(field.base_field.max_length, 32)
                self.assertEqual(field.get_default(), [])
