# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RevenueRecognitionAccount(models.Model):
    _name = "revenue_recognition_account"
    _description = "Revenue Recognition Account Mapping"

    recognition_id = fields.Many2one(
        string="# Recognition",
        comodel_name="revenue_recognition",
        required=True,
        ondelete="cascade",
    )
    wip_account_id = fields.Many2one(
        string="WIP Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
    )
    expense_account_id = fields.Many2one(
        string="Expense Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
    )
    company_currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="recognition_id.company_currency_id",
    )
    debit = fields.Monetary(
        string="Debit",
        required=True,
        currency_field="company_currency_id",
        default=0.0,
    )
    credit = fields.Monetary(
        string="Credit",
        required=True,
        currency_field="company_currency_id",
        default=0.0,
    )
    balance = fields.Monetary(
        string="Balance",
        currency_field="company_currency_id",
        compute="_compute_balance",
        store=True,
    )
    budget = fields.Monetary(
        string="Budget",
        required=True,
        currency_field="company_currency_id",
        default=0.0,
    )
    theoritical_balance = fields.Monetary(
        string="Theoritical Balance",
        currency_field="company_currency_id",
        compute="_compute_theoritical_balance",
        store=True,
    )
    percent_realized = fields.Float(
        string="Percent Realized",
        compute="_compute_percent_realized",
        store=True,
    )
    debit_move_line_id = fields.Many2one(
        string="Debit Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )
    credit_move_line_id = fields.Many2one(
        string="Credit Move Line",
        comodel_name="account.move.line",
        readonly=True,
    )

    @api.depends(
        "debit",
        "credit",
    )
    def _compute_balance(self):
        for record in self:
            record.balance = record.debit - record.credit

    @api.depends(
        "balance",
        "budget",
    )
    def _compute_percent_realized(self):
        for record in self:
            percent_realized = 0.0
            try:
                percent_realized = record.balance / record.budget
            except Exception:
                percent_realized = 0.0
            record.percent_realized = percent_realized * 100.00

    @api.depends("budget", "recognition_id.percentage_accepted")
    def _compute_theoritical_balance(self):
        for record in self:
            record.theoritical_balance = (
                record.recognition_id.percentage_accepted / 100.00
            ) * record.budget

    def _create_wip_ml_point_in_time(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_wip_ml_point_in_time()
        )

    def _create_expense_ml_point_in_time(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_expense_ml_point_in_time()
        )

    def _create_wip_ml_over_time_output(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_wip_ml_over_time_output()
        )

    def _create_expense_ml_over_time_output(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_expense_ml_over_time_output()
        )

    def _create_wip_ml_over_time_input(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_wip_ml_over_time_input()
        )

    def _create_expense_ml_over_time_input(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_expense_ml_over_time_input()
        )

    def _prepare_wip_ml_point_in_time(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.wip_account_id,
            debit=0.0,
            credit=self.balance,
        )

    def _prepare_expense_ml_point_in_time(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.expense_account_id,
            debit=self.balance,
            credit=0.0,
        )

    def _prepare_wip_ml_over_time_output(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.wip_account_id,
            debit=0.0,
            credit=self.theoritical_balance,
        )

    def _prepare_expense_ml_over_time_output(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.expense_account_id,
            debit=self.theoritical_balance,
            credit=0.0,
        )

    def _prepare_wip_ml_over_time_input(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.wip_account_id,
            debit=0.0,
            credit=self.balance,
        )

    def _prepare_expense_ml_over_time_input(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.expense_account_id,
            debit=self.balance,
            credit=0.0,
        )

    def _prepare_ml(self, account, debit, credit):
        pob = self.recognition_id.performance_obligation_id
        return {
            "account_id": account.id,
            "partner_id": pob.partner_id.id,
            "analytic_account_id": pob.analytic_account_id.id,
            "debit": debit,
            "credit": credit,
            "move_id": self.recognition_id.move_id.id,
        }
