from psycopg2.errors import NotNullViolation

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase


class TestBulkIncomeAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.old_income_account = cls.env["account.account"].create(
            {
                "name": "Old Income",
                "code": "TCK9.OLD",
                "account_type": "income",
            }
        )
        cls.new_income_account = cls.env["account.account"].create(
            {
                "name": "New Income",
                "code": "TCK9.NEW",
                "account_type": "income",
            }
        )
        if not cls.env["account.journal"].search([("type", "=", "sale")], limit=1):
            cls.env["account.journal"].create(
                {"name": "Customer Invoices", "type": "sale", "code": "TCK9INV"}
            )
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    (0, 0, {"display_type": "line_section", "name": "Section"}),
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "quantity": 1,
                            "price_unit": 100,
                            "account_id": cls.old_income_account.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Line 2",
                            "quantity": 1,
                            "price_unit": 200,
                            "account_id": cls.old_income_account.id,
                        },
                    ),
                ],
            }
        )

    def test_apply_updates_product_lines_only(self):
        wizard = self.env["account.move.bulk.income.account.wizard"].create(
            {
                "move_id": self.invoice.id,
                "income_account_id": self.new_income_account.id,
            }
        )
        wizard.action_apply()

        product_lines = self.invoice.invoice_line_ids.filtered(lambda l: l.display_type == "product")
        self.assertEqual(len(product_lines), 2)
        self.assertTrue(all(l.account_id == self.new_income_account for l in product_lines))

        section_line = self.invoice.invoice_line_ids.filtered(lambda l: l.display_type == "line_section")
        self.assertNotEqual(section_line.account_id, self.new_income_account)

    def test_apply_blocked_on_posted_invoice(self):
        self.invoice.action_post()
        wizard = self.env["account.move.bulk.income.account.wizard"].create(
            {
                "move_id": self.invoice.id,
                "income_account_id": self.new_income_account.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_apply_noop_on_invoice_with_no_product_lines(self):
        empty_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (0, 0, {"display_type": "line_section", "name": "Section only"}),
                ],
            }
        )
        wizard = self.env["account.move.bulk.income.account.wizard"].create(
            {
                "move_id": empty_invoice.id,
                "income_account_id": self.new_income_account.id,
            }
        )
        wizard.action_apply()  # should not raise, simply no lines to update

    def test_income_account_required(self):
        with self.assertRaises(NotNullViolation):
            self.env["account.move.bulk.income.account.wizard"].create(
                {"move_id": self.invoice.id}
            )

    def test_account_rejected_from_other_company(self):
        other_company = self.env["res.company"].create({"name": "Other Co"})
        other_company_account = self.env["account.account"].create(
            {
                "name": "Other Co Income",
                "code": "TCK9.OTHER",
                "account_type": "income",
                "company_ids": [(6, 0, [other_company.id])],
            }
        )
        wizard = self.env["account.move.bulk.income.account.wizard"].create(
            {
                "move_id": self.invoice.id,
                "income_account_id": other_company_account.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_access_denied_without_invoicing_group(self):
        billing_group = self.env.ref("account.group_account_invoice")
        restricted_user = self.env["res.users"].create(
            {
                "name": "No Invoicing Access",
                "login": "tck9_no_invoicing_access",
                "email": "tck9_no_invoicing_access@example.com",
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        self.assertNotIn(billing_group, restricted_user.group_ids)
        with self.assertRaises(AccessError):
            self.env["account.move.bulk.income.account.wizard"].with_user(restricted_user).create(
                {
                    "move_id": self.invoice.id,
                    "income_account_id": self.new_income_account.id,
                }
            )
