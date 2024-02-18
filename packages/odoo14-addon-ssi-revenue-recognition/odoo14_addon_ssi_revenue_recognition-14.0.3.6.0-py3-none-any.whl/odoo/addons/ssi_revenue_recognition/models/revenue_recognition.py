# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class RevenueRecognition(models.Model):
    _name = "revenue_recognition"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.date_duration",
    ]
    _description = "Revenue Recognition"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    # Mixin duration attribute
    _date_start_readonly = True
    _date_end_readonly = True
    _date_start_required = True
    _date_end_required = True
    _date_start_states_list = ["draft"]
    _date_start_states_readonly = ["draft"]
    _date_end_states_list = ["draft"]
    _date_end_states_readonly = ["draft"]

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    type_id = fields.Many2one(
        string="Type",
        comodel_name="revenue_recognition_type",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        domain=[
            ("parent_id", "=", False),
        ],
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    contract_id = fields.Many2one(
        string="# Contract",
        comodel_name="service.contract",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    performance_obligation_id = fields.Many2one(
        string="# Performance Obligation",
        comodel_name="service_contract.performance_obligation",
        required=True,
        readonly=True,
        ondelete="restrict",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        related="performance_obligation_id.analytic_account_id",
        store=True,
    )
    quantity = fields.Float(
        string="Quantity",
        related="performance_obligation_id.quantity",
        store=True,
    )
    quantity_accepted = fields.Float(
        string="Quantity Accepted",
        compute="_compute_quantity_accepted",
        store=True,
    )
    quantity_diff = fields.Float(
        string="Quantity Diff.",
        compute="_compute_quantity_accepted",
        store=True,
    )
    percentage_accepted = fields.Float(
        string="Percentage Accepted",
        compute="_compute_quantity_accepted",
        store=True,
    )
    amount_accepted = fields.Monetary(
        string="Amount Accepted",
        compute="_compute_quantity_accepted",
        store=True,
        currency_field="company_currency_id",
    )
    analytic_budget_id = fields.Many2one(
        string="# Analytic Budget",
        comodel_name="analytic_budget.budget",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    product_id = fields.Many2one(
        string="Product",
        related="performance_obligation_id.product_id",
    )
    move_line_ids = fields.Many2many(
        string="Move Lines",
        comodel_name="account.move.line",
        relation="rel_revenue_recognition_2_move_line",
        column1="recognition_id",
        column2="line_id",
        readonly=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_ids = fields.One2many(
        string="Account Mappings",
        comodel_name="revenue_recognition_account",
        inverse_name="recognition_id",
    )
    amount_budgeted = fields.Monetary(
        string="Amount Budgeted",
        currency_field="company_currency_id",
        compute="_compute_budget",
        store=True,
    )
    amount_realized = fields.Monetary(
        string="Amount Realized",
        currency_field="company_currency_id",
        compute="_compute_budget",
        store=True,
    )
    percent_realized = fields.Float(
        string="Percentage Realized",
        compute="_compute_budget",
        store=True,
    )
    theoritical_accepted = fields.Monetary(
        string="Amount Accepted (Theoritical)",
        currency_field="company_currency_id",
        compute="_compute_budget",
        store=True,
    )
    wip_account_ids = fields.Many2many(
        string="WIP Accounts",
        related="type_id.wip_account_ids",
    )
    expense_account_ids = fields.Many2many(
        string="Expense Accounts",
        related="type_id.expense_account_ids",
    )
    performance_obligation_acceptance_ids = fields.One2many(
        string="Performance Obligation Acceptances",
        comodel_name="performance_obligation_acceptance",
        inverse_name="revenue_recognition_id",
        readonly=True,
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        ondelete="restrict",
    )
    unearned_income_account_id = fields.Many2one(
        string="Unearned Income Account",
        comodel_name="account.account",
        ondelete="restrict",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    income_account_id = fields.Many2one(
        string="Income Account",
        comodel_name="account.account",
        ondelete="restrict",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move",
        readonly=True,
    )

    @api.model
    def _get_policy_field(self):
        res = super(RevenueRecognition, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.depends(
        "quantity",
        "performance_obligation_acceptance_ids",
        "performance_obligation_acceptance_ids.state",
        "performance_obligation_acceptance_ids.qty_fulfilled",
    )
    def _compute_quantity_accepted(self):
        for record in self:
            qty_accepted = qty_diff = percentage = amount_accepted = 0.0
            for acceptance in record.performance_obligation_acceptance_ids.filtered(
                lambda r: r.state == "done"
            ):
                qty_accepted += acceptance.qty_fulfilled

            qty_diff = record.quantity - qty_accepted
            try:
                percentage = (qty_accepted / record.quantity) * 100.00
                amount_accepted = (
                    qty_accepted / record.quantity
                ) * record.performance_obligation_id.price_subtotal
            except Exception:
                percentage = 0.0
            record.quantity_accepted = qty_accepted
            record.quantity_diff = qty_diff
            record.percentage_accepted = percentage
            record.amount_accepted = amount_accepted

    @api.depends(
        "account_ids",
        "account_ids.budget",
        "account_ids.balance",
        "performance_obligation_id",
        "performance_obligation_id.price_subtotal",
    )
    def _compute_budget(self):
        for record in self:
            budgeted = realized = percentage = theoritical_accepted = 0.0
            for account in record.account_ids:
                budgeted += account.budget
                realized += account.balance
            try:
                percentage = (realized / budgeted) * 100.00
                theoritical_accepted = (
                    realized / budgeted
                ) * record.performance_obligation_id.price_subtotal
            except Exception:
                pass
            record.amount_budgeted = budgeted
            record.amount_realized = realized
            record.percent_realized = percentage
            record.theoritical_accepted = theoritical_accepted

    @api.onchange(
        "type_id",
    )
    def onchange_journal_id(self):
        if self.type_id:
            self.journal_id = self.type_id.journal_id.id

    @api.onchange(
        "type_id",
    )
    def onchange_policy_template_id(self):
        template_id = self._get_template_policy()
        self.policy_template_id = template_id

    @api.onchange(
        "partner_id",
    )
    def onchange_contract_id(self):
        self.contract_id = False

    @api.onchange(
        "contract_id",
    )
    def onchange_performance_obligation_id(self):
        self.performance_obligation_id = False

    @api.onchange("type_id")
    def onchange_account_ids(self):
        self.update({"account_ids": [(5, 0, 0)]})
        cost = []
        if self.type_id:
            for detail in self.type_id.account_ids:
                cost.append(
                    (
                        0,
                        0,
                        {
                            "wip_account_id": detail.wip_account_id.id,
                            "expense_account_id": detail.expense_account_id.id,
                        },
                    )
                )
            self.update({"account_ids": cost})

    @api.onchange(
        "type_id",
    )
    def onchange_unearned_income_account_id(self):
        self.unearned_income_account_id = False
        if self.type_id:
            self.unearned_income_account_id = self.product_id._get_product_account(
                self.type_id.unearned_income_usage_id.code
            )

    @api.onchange(
        "type_id",
    )
    def onchange_income_account_id(self):
        self.income_account_id = False
        if self.type_id:
            self.income_account_id = self.product_id._get_product_account(
                self.type_id.income_usage_id.code
            )

    def action_populate(self):
        for record in self:
            record._populate_pob_acceptances()
            record._populate_wip_move_line()

    def _populate_pob_acceptances(self):
        self.ensure_one()
        self.performance_obligation_acceptance_ids.write(
            {
                "revenue_recognition_id": False,
            }
        )
        POBAcceptance = self.env["performance_obligation_acceptance"]
        pob_acceptances = POBAcceptance.search(self._prepare_pob_acceptance_domain())
        pob_acceptances.write(
            {
                "revenue_recognition_id": self.id,
            }
        )

    def _prepare_pob_acceptance_domain(self):
        self.ensure_one()

        return [
            ("performance_obligation_id", "=", self.performance_obligation_id.id),
            ("date", "<=", self.date),
            ("state", "=", "done"),
            ("revenue_recognition_id", "=", False),
        ]

    def _populate_wip_move_line(self):
        self.ensure_one()

        MoveLine = self.env["account.move.line"]
        move_lines = MoveLine.search(self._prepare_move_line_domain())
        self.write({"move_line_ids": [(6, 0, move_lines.ids)]})
        self._compute_balance()

    def _prepare_move_line_domain(self):
        self.ensure_one()
        pob = self.performance_obligation_id
        return [
            ("analytic_account_id", "=", pob.analytic_account_id.id),
            ("account_id", "in", self.wip_account_ids.ids),
            ("move_id.state", "=", "posted"),
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
        ]

    def _compute_balance(self):
        self.ensure_one()
        MoveLine = self.env["account.move.line"]
        BudgetCostSummary = self.env["analytic_budget.cost_summary_account"]
        for account in self.account_ids:
            data = {}
            criteria = [
                ("id", "in", self.move_line_ids.ids),
                ("account_id", "=", account.wip_account_id.id),
                ("date", ">=", self.date_start),
                ("date", "<=", self.date_end),
            ]
            results = MoveLine.read_group(
                criteria, ["account_id", "debit", "credit"], ["account_id"], False
            )
            if len(results) > 0:
                data.update(
                    {
                        "debit": results[0]["debit"],
                        "credit": results[0]["credit"],
                    }
                )
            cost_summary_criteria = [
                ("budget_id", "=", self.analytic_budget_id.id),
                ("account_id", "=", account.expense_account_id.id),
            ]
            cost_summaries = BudgetCostSummary.search(cost_summary_criteria)
            if len(cost_summaries) > 0:
                data.update(
                    {
                        "budget": cost_summaries[0].amount_budgeted,
                    }
                )
            account.write(data)

    @ssi_decorator.post_done_action()
    def _create_accounting_entry(self):
        pob = self.performance_obligation_id
        self._create_move()
        if pob.revenue_recognition_timing == "point_in_time":
            self._create_move_point_in_time()
        elif (
            pob.revenue_recognition_timing == "over_time"
            and pob.progress_completion_method == "input"
        ):
            self._create_move_over_time_input()
        elif (
            pob.revenue_recognition_timing == "over_time"
            and pob.progress_completion_method == "output"
        ):
            self._create_move_over_time_output()
        self.move_id.action_post()

    def _create_move(self):
        self.ensure_one()
        Move = self.env["account.move"]
        move = Move.with_context(check_move_validity=False).create(
            self._prepare_account_move()
        )
        self.write(
            {
                "move_id": move.id,
            }
        )

    def _create_move_point_in_time(self):
        self.ensure_one()
        self._create_unearned_income_ml_point_in_time()
        self._create_income_ml_point_in_time()
        for account in self.account_ids:
            account._create_wip_ml_point_in_time()
            account._create_expense_ml_point_in_time()

    def _create_unearned_income_ml_point_in_time(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_unearned_income_ml_point_in_time()
        )

    def _create_income_ml_point_in_time(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_income_ml_point_in_time()
        )

    def _prepare_unearned_income_ml_point_in_time(self):
        self.ensure_one()
        pob = self.performance_obligation_id
        return self._prepare_ml(
            account=self.unearned_income_account_id,
            debit=pob.price_subtotal,
            credit=0.0,
        )

    def _prepare_income_ml_point_in_time(self):
        self.ensure_one()
        pob = self.performance_obligation_id
        return self._prepare_ml(
            account=self.income_account_id,
            debit=0.0,
            credit=pob.price_subtotal,
        )

    def _create_move_over_time_input(self):
        self.ensure_one()
        self._create_unearned_income_ml_over_time_input()
        self._create_income_ml_over_time_input()
        for account in self.account_ids:
            account._create_wip_ml_over_time_input()
            account._create_expense_ml_over_time_input()

    def _create_move_over_time_output(self):
        self.ensure_one()
        self._create_unearned_income_ml_over_time_output()
        self._create_income_ml_over_time_output()
        for account in self.account_ids:
            account._create_wip_ml_over_time_output()
            account._create_expense_ml_over_time_output()

    def _create_unearned_income_ml_over_time_output(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_unearned_income_ml_over_time_output()
        )

    def _create_income_ml_over_time_output(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_income_ml_over_time_output()
        )

    def _prepare_unearned_income_ml_over_time_output(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.unearned_income_account_id,
            debit=self.amount_accepted,
            credit=0.0,
        )

    def _prepare_income_ml_over_time_output(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.income_account_id,
            debit=0.0,
            credit=self.amount_accepted,
        )

    def _create_unearned_income_ml_over_time_input(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_unearned_income_ml_over_time_input()
        )

    def _create_income_ml_over_time_input(self):
        ML = self.env["account.move.line"]
        ML.with_context(check_move_validity=False).create(
            self._prepare_income_ml_over_time_input()
        )

    def _prepare_unearned_income_ml_over_time_input(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.unearned_income_account_id,
            debit=self.theoritical_accepted,
            credit=0.0,
        )

    def _prepare_income_ml_over_time_input(self):
        self.ensure_one()
        return self._prepare_ml(
            account=self.income_account_id,
            debit=0.0,
            credit=self.theoritical_accepted,
        )

    def _prepare_account_move(self):
        return {
            "name": self.name,
            "date": self.date,
            "journal_id": self.journal_id.id,
        }

    def _create_income_move_lines(self):
        self.ensure_one()
        ML = self.env["account.move.line"]

        ML.with_context(check_move_validity=False).create(
            self._prepare_unearned_income_ml()
        )
        ML.with_context(check_move_validity=False).create(self._prepare_income_ml())

    def _prepare_ml(self, account, debit, credit):
        pob = self.performance_obligation_id
        return {
            "account_id": account.id,
            "partner_id": self.partner_id.id,
            "analytic_account_id": pob.analytic_account_id.id,
            "debit": debit,
            "credit": credit,
            "move_id": self.move_id.id,
        }

    @ssi_decorator.post_cancel_action()
    def _20_cancel_move(self):
        self.ensure_one()

        if not self.move_id:
            return True

        move = self.move_id
        self.write(
            {
                "move_id": False,
            }
        )

        if move.state == "posted":
            move.button_cancel()

        move.with_context(force_delete=True).unlink()

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
