# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _name = "account.analytic.account"
    _inherit = ["account.analytic.account"]

    revenue_recognition_type = fields.Selection(
        string="Revenue Recognition Type",
        selection=[
            ("full", "Full"),
            ("periodic", "Periodic"),
        ],
    )
    progress_completion_method = fields.Selection(
        string="Progress Completion Method",
        selection=[
            ("input", "Input"),
            ("output", "Output"),
        ],
        required=True,
        default="input",
    )
