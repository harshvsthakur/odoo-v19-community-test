from odoo import fields, models
from odoo.exceptions import UserError


class AccountMoveBulkIncomeAccountWizard(models.TransientModel):
    _name = "account.move.bulk.income.account.wizard"
    _description = "Bulk-update income account on an invoice's lines"

    move_id = fields.Many2one("account.move", required=True, readonly=True)
    income_account_id = fields.Many2one(
        "account.account",
        string="Income Account",
        required=True,
        domain=[("account_type", "=", "income")],
    )

    def action_apply(self):
        self.ensure_one()
        if self.move_id.move_type != "out_invoice" or self.move_id.state != "draft":
            raise UserError(
                "The income account can only be bulk-updated on a draft Customer Invoice."
            )
        if self.move_id.company_id not in self.income_account_id.company_ids:
            raise UserError(
                "The selected income account does not belong to this invoice's company."
            )
        lines = self.move_id.invoice_line_ids.filtered(lambda l: l.display_type == "product")
        lines.write({"account_id": self.income_account_id.id})
        return {"type": "ir.actions.act_window_close"}
