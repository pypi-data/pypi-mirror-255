# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RevenueRecognitionType(models.Model):
    _name = "revenue_recognition_type"
    _inherit = ["mixin.master_data"]
    _description = "Revenue Recognition Type"

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
    )
    unearned_income_usage_id = fields.Many2one(
        string="Unearned Income Usage",
        comodel_name="product.usage_type",
        required=True,
        ondelete="restrict",
    )
    income_usage_id = fields.Many2one(
        string="Unearned Income Usage",
        comodel_name="product.usage_type",
        required=True,
        ondelete="restrict",
    )
    account_ids = fields.One2many(
        string="Account Mappings",
        comodel_name="revenue_recognition_type_account",
        inverse_name="type_id",
    )
    wip_account_ids = fields.Many2many(
        string="WIP Accounts",
        comodel_name="account.account",
        compute="_compute_account",
    )
    expense_account_ids = fields.Many2many(
        string="Expense Accounts",
        comodel_name="account.account",
        compute="_compute_account",
    )

    @api.depends(
        "account_ids",
        "account_ids.wip_account_id",
        "account_ids.expense_account_id",
    )
    def _compute_account(self):
        for record in self:
            wip_accounts = expense_accounts = self.env["account.account"]
            if record.account_ids:
                wip_accounts = record.account_ids.mapped("wip_account_id")
                expense_accounts = record.account_ids.mapped("expense_account_id")
            record.wip_account_ids = wip_accounts.ids
            record.expense_account_ids = expense_accounts.ids
