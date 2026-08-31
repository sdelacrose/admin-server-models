from importlib import import_module

from django.test import SimpleTestCase

from models.constants import (
    CUSTOMER_DEMAND_DOCUMENT_TYPE,
    GC_COMPANY_DOCUMENT_TYPES,
)


migration = import_module(
    "models.migrations.0121_add_customer_demand_company_document_type"
)


class CustomerDemandCompanyDocumentTypeTests(SimpleTestCase):
    def test_company_defaults_include_customer_demand_before_other(self):
        self.assertIn(CUSTOMER_DEMAND_DOCUMENT_TYPE, GC_COMPANY_DOCUMENT_TYPES)
        self.assertLess(
            GC_COMPANY_DOCUMENT_TYPES.index(CUSTOMER_DEMAND_DOCUMENT_TYPE),
            GC_COMPANY_DOCUMENT_TYPES.index("Other:OTH"),
        )

    def test_backfill_preserves_custom_values_and_inserts_before_other(self):
        current = ["General:GEN", "Company Specific:CSP", "Other:OTH"]

        self.assertEqual(
            migration.ensure_customer_demand_document_type(current),
            [
                "General:GEN",
                "Company Specific:CSP",
                CUSTOMER_DEMAND_DOCUMENT_TYPE,
                "Other:OTH",
            ],
        )

    def test_backfill_is_idempotent_for_coded_and_legacy_values(self):
        coded = ["General:GEN", CUSTOMER_DEMAND_DOCUMENT_TYPE, "Other:OTH"]
        legacy = ["General:GEN", "Customer Demand", "Other:OTH"]

        self.assertEqual(
            migration.ensure_customer_demand_document_type(coded),
            coded,
        )
        self.assertEqual(
            migration.ensure_customer_demand_document_type(legacy),
            legacy,
        )

    def test_backfill_handles_empty_values(self):
        self.assertEqual(
            migration.ensure_customer_demand_document_type(None),
            [CUSTOMER_DEMAND_DOCUMENT_TYPE],
        )
