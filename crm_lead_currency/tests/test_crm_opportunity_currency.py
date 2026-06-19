# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import TransactionCase

from ..hooks import post_init_hook


class TestCrmOpportunityCurrency(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lead = cls.env["crm.lead"].create({"name": "test lead"})
        cls.foreign_currency = cls.env["res.currency"].search(
            [("id", "!=", cls.lead.company_currency.id)],
            limit=1,
        )
        cls.other_company = cls.env["res.company"].create(
            {
                "name": "Foreign Currency Company",
                "currency_id": cls.foreign_currency.id,
            }
        )

    def test_is_same_currency(self):
        self.lead.customer_currency_id = self.lead.company_currency
        self.assertTrue(self.lead.is_same_currency)
        self.lead.customer_currency_id = self.foreign_currency
        self.assertFalse(self.lead.is_same_currency)

    def test_same_currency_expected_revenue_not_updated(self):
        self.lead.customer_currency_id = self.lead.company_currency
        self.lead.expected_revenue = 100
        self.lead.amount_customer_currency = 124
        self.lead._onchange_currency()
        self.assertEqual(self.lead.expected_revenue, 100)

    def test_different_currency_expected_revenue_updated(self):
        self.lead.expected_revenue = 100
        self.lead.customer_currency_id = self.foreign_currency
        self.lead.amount_customer_currency = 124
        self.lead._onchange_currency()
        self.assertNotEqual(self.lead.expected_revenue, 100)

    def test_post_init_hook_sets_missing_customer_currency(self):
        lead = self.env["crm.lead"].create({"name": "lead without customer currency"})
        lead.customer_currency_id = False

        post_init_hook(self.env)

        lead.invalidate_recordset(["customer_currency_id"])
        self.assertEqual(lead.customer_currency_id, lead.company_currency)

    def test_post_init_hook_replaces_install_default_with_company_currency(self):
        lead = self.env["crm.lead"].create(
            {
                "name": "lead with install default currency",
                "company_id": self.other_company.id,
            }
        )
        lead.customer_currency_id = self.env.company.currency_id

        post_init_hook(self.env)

        lead.invalidate_recordset(["customer_currency_id"])
        self.assertEqual(lead.customer_currency_id, lead.company_currency)
