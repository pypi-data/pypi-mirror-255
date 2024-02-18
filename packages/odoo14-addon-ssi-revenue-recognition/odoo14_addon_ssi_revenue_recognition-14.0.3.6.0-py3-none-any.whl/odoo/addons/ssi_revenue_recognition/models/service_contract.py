# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class ServiceContract(models.Model):
    _name = "service.contract"
    _inherit = ["service.contract"]

    pob_analytic_group_id = fields.Many2one(
        string="POb Analytic Group",
        comodel_name="account.analytic.group",
    )
    analytic_budget_id = fields.Many2one(
        string="# Analytic Budget",
        comodel_name="analytic_budget.budget",
    )
    lock_budget = fields.Boolean(
        string="Lock Budget",
        default=False,
        readonly=True,
    )
    performance_obligation_ids = fields.One2many(
        string="Performance Obligations",
        comodel_name="service_contract.performance_obligation",
        inverse_name="contract_id",
        readonly=True,
    )
    amount_total_pob = fields.Monetary(
        string="Total Performance Obligation",
        currency_field="currency_id",
        compute="_compute_amount_pob",
        store=True,
    )
    amount_diff_pob = fields.Monetary(
        string="Performance Obligation Diff",
        currency_field="currency_id",
        compute="_compute_amount_pob",
        store=True,
    )

    @api.depends(
        "performance_obligation_ids",
        "performance_obligation_ids.price_subtotal",
    )
    def _compute_amount_pob(self):
        for record in self:
            total = diff = 0.0
            for pob in record.performance_obligation_ids:
                total += pob.price_subtotal
            diff = record.amount_untaxed - total
            record.amount_total_pob = total
            record.amount_diff_pob = diff

    @api.onchange(
        "analytic_account_id",
    )
    def onchange_analytic_budget_id(self):
        self.analytic_budget_id = False

    @api.onchange(
        "type_id",
    )
    def onchange_pob_analytic_group_id(self):
        self.pob_analytic_group_id = False
        if self.type_id:
            self.pob_analytic_group_id = self.type_id.pob_analytic_group_id

    def action_lock_budget(self):
        for record in self.sudo():
            record._lock_budget()

    def action_unlock_budget(self):
        for record in self.sudo():
            record._unlock_budget()

    @ssi_decorator.post_confirm_action()
    def _11_confirm_performance_obligation(self):
        for pob in self.performance_obligation_ids:
            pob.action_confirm()

    @ssi_decorator.post_approve_action()
    def _11_approve_performance_obligation(self):
        for pob in self.performance_obligation_ids:
            pob.action_approve_approval()

    @ssi_decorator.post_reject_action()
    def _11_reject_performance_obligation(self):
        for pob in self.performance_obligation_ids:
            pob.action_reject_approval()

    # @ssi_decorator.post_open_action()
    # def _11_approve_performance_obligation(self):
    #     for pob in self.performance_obligation_ids:
    #         pob.action_approve_approval()

    @ssi_decorator.post_cancel_action()
    def _11_cancel_performance_obligation(self):
        for pob in self.performance_obligation_ids:
            pob.action_cancel()

    @ssi_decorator.post_restart_action()
    def _11_done_performance_obligation(self):
        for pob in self.performance_obligation_ids:
            pob.action_restart()

    # @ssi_decorator.post_open_action()
    # def _11_create_pob_analytic_account(self):
    #     for pob in self.performance_obligation_ids:
    #         pob._create_analytic_account()

    def _lock_budget(self):
        self.ensure_one()
        self.write(
            {
                "lock_budget": True,
            }
        )

    def _unlock_budget(self):
        self.ensure_one()
        self.write(
            {
                "lock_budget": False,
            }
        )
