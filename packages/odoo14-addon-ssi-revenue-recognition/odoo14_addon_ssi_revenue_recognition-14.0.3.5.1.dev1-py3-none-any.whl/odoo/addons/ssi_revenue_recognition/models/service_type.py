# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class ServiceType(models.Model):
    _name = "service.type"
    _inherit = [
        "service.type",
    ]

    pob_analytic_group_id = fields.Many2one(
        string="POb Analytic Group",
        comodel_name="account.analytic.group",
    )
