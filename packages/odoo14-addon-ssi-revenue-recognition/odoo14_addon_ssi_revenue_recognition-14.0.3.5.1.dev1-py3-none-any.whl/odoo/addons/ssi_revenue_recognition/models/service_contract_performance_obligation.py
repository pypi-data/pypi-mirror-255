# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class ServiceContractPerformanceObligation(models.Model):
    _name = "service_contract.performance_obligation"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.product_line_price",
    ]
    _description = "Service Contract Performance Obligation"

    _automatically_insert_view_element = True

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Policy fields visibility
    _automatically_insert_open_policy_fields = False
    _automatically_insert_done_policy_fields = False

    # Button visibility
    _automatically_insert_done_button = False
    _automatically_insert_open_button = False

    # Sequence attribute
    _create_sequence_state = "open"

    _statusbar_visible_label = "draft,open,done"
    _policy_field_order = [
        "open_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
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
        "dom_open",
        "dom_done",
        "dom_cancel",
    ]

    contract_id = fields.Many2one(
        string="# Contract",
        comodel_name="service.contract",
        required=True,
        ondelete="cascade",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    partner_id = fields.Many2one(
        string="Partner",
        related="contract_id.partner_id",
        store=True,
    )
    title = fields.Char(
        string="Title",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date = fields.Date(
        string="Date",
        related="contract_id.date",
        store=True,
    )
    product_id = fields.Many2one(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    currency_id = fields.Many2one(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    uom_quantity = fields.Float(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    uom_id = fields.Many2one(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    pricelist_id = fields.Many2one(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    price_unit = fields.Monetary(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    progress_completion_method = fields.Selection(
        string="Progress Completion Method",
        selection=[
            ("input", "Input"),
            ("output", "Output"),
        ],
        required=True,
        default="input",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    revenue_recognition_timing = fields.Selection(
        string="Revenue Recognition Timing",
        selection=[
            ("over_time", "Over Time"),
            ("point_in_time", "At a Point in Time"),
        ],
        required=True,
        default="over_time",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_start = fields.Date(
        string="Date Start",
    )
    date_end = fields.Date(
        string="Date Start",
    )
    require_date = fields.Boolean(
        string="Require Date",
        compute="_compute_date_attribute",
        store=False,
    )
    readonly_date = fields.Boolean(
        string="Readonly Date",
        compute="_compute_date_attribute",
        store=False,
    )
    invisible_date = fields.Boolean(
        string="Invisible Date",
        compute="_compute_date_attribute",
        store=False,
    )
    fulfillment_field_id = fields.Many2one(
        string="Fulfillment Field",
        comodel_name="ir.model.fields",
        domain=[
            ("model_id.model", "=", "performance_obligation_acceptance"),
            ("ttype", "=", "float"),
            ("name", "!=", "qty_fulfilled"),
        ],
        required=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    acceptance_ids = fields.One2many(
        string="Performance Obligation Acceptances",
        comodel_name="performance_obligation_acceptance",
        inverse_name="performance_obligation_id",
        readonly=True,
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
        currency_field="currency_id",
    )

    @api.model
    def _get_policy_field(self):
        res = super(ServiceContractPerformanceObligation, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "open_ok",
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
        "revenue_recognition_timing",
        "state",
    )
    def _compute_date_attribute(self):
        for record in self:
            required = invisible = readonly = False
            if record.revenue_recognition_timing == "point_in_time":
                required = True
            else:
                invisible = True

            if record.state != "draft":
                readonly = True
            record.require_date = required
            record.readonly_date = readonly
            record.invisible_date = invisible

    @api.depends(
        "quantity",
        "acceptance_ids",
        "acceptance_ids.state",
        "acceptance_ids.qty_fulfilled",
    )
    def _compute_quantity_accepted(self):
        for record in self:
            qty_accepted = qty_diff = percentage = amount_accepted = 0.0
            for acceptance in record.acceptance_ids.filtered(
                lambda r: r.state == "done"
            ):
                qty_accepted += acceptance.qty_fulfilled

            qty_diff = record.quantity - qty_accepted
            try:
                percentage = (qty_accepted / record.quantity) * 100.00
                amount_accepted = (
                    qty_accepted / record.quantity
                ) * record.price_subtotal
            except Exception:
                percentage = 0.0
            record.quantity_accepted = qty_accepted
            record.quantity_diff = qty_diff
            record.percentage_accepted = percentage
            record.amount_accepted = amount_accepted

    @api.onchange(
        "revenue_recognition_timing",
    )
    def onchange_date_start(self):
        self.date_start = False

    @api.onchange(
        "revenue_recognition_timing",
    )
    def onchange_date_end(self):
        self.date_end = False

    @api.onchange("product_id")
    def onchange_name(self):
        pass

    @api.onchange("product_id")
    def onchange_title(self):
        self.title = False
        if self.product_id:
            self.title = self.product_id.display_name

    @ssi_decorator.post_open_action()
    def _10_create_analytic_account(self):
        self.ensure_one()
        if self.analytic_account_id:
            self._update_analytic_account()
        else:
            AA = self.env["account.analytic.account"]
            aa = AA.create(self._prepare_analytic_account())
            self.write(
                {
                    "analytic_account_id": aa.id,
                }
            )

    def _update_analytic_account(self):
        self.ensure_one()
        self.analytic_account_id.write(self._prepare_update_analytic_account())

    def _prepare_update_analytic_account(self):
        self.ensure_one()
        contract = self.contract_id
        if contract.pob_analytic_group_id:
            group_id = contract.pob_analytic_group_id.id
        elif contract.analytic_group_id:
            group_id = contract.analytic_group_id.id
        else:
            group_id = False
        return {
            "name": self.title,
            "code": self.name,
            "partner_id": contract.partner_id.id,
            "group_id": group_id,
            "date_start": self.date_start,
            "date_end": self.date_end,
        }

    def _prepare_analytic_account(self):
        self.ensure_one()
        contract = self.contract_id
        if contract.pob_analytic_group_id:
            group_id = contract.pob_analytic_group_id.id
        elif contract.analytic_group_id:
            group_id = contract.analytic_group_id.id
        else:
            group_id = False
        return {
            "name": self.title,
            "code": self.name,
            "partner_id": contract.partner_id.id,
            "group_id": group_id,
            "date_start": self.date_start,
            "date_end": self.date_end,
        }

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
