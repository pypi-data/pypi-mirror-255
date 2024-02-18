# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class RevenueRecognitionFull(models.Model):
    _name = "revenue_recognition_full"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.company_currency",
    ]
    _description = "Revenue Recognition (Full)"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

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
        comodel_name="revenue_recognition_full_type",
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
        comodel_name="account.analytic.account",
        required=True,
        readonly=True,
        ondelete="restrict",
        domain=[
            ("revenue_recognition_type", "=", "full"),
        ],
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    move_line_ids = fields.Many2many(
        string="Move Lines",
        comodel_name="account.move.line",
        relation="rel_revenue_recognition_full_2_move_line",
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
        comodel_name="revenue_recognition_full_account",
        inverse_name="recognition_id",
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
    move_id = fields.Many2one(
        string="# Move",
        comodel_name="account.move",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        default="draft",
        required=True,
        readonly=True,
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
    )

    @api.model
    def _get_policy_field(self):
        res = super(RevenueRecognitionFull, self)._get_policy_field()
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
                            "accrue_account_id": detail.accrue_account_id.id,
                            "account_id": detail.account_id.id,
                            "direction": detail.direction,
                        },
                    )
                )
            self.update({"account_ids": cost})

    def action_populate(self):
        for record in self:
            record._populate()

    def _populate(self):
        self.ensure_one()

        MoveLine = self.env["account.move.line"]
        move_lines = MoveLine.search(self._prepare_move_line_domain())
        self.write({"move_line_ids": [(6, 0, move_lines.ids)]})
        self._compute_balance()

    def _prepare_move_line_domain(self):
        accounts = self.account_ids.mapped("accrue_account_id")
        return [
            ("analytic_account_id", "=", self.analytic_account_id.id),
            ("account_id", "in", accounts.ids),
            ("move_id.state", "=", "posted"),
            ("reconciled", "=", False),
        ]

    def _compute_balance(self):
        self.ensure_one()
        self.account_ids.mapped("account_id")

        MoveLine = self.env["account.move.line"]
        for account in self.account_ids:
            criteria = [
                ("id", "in", self.move_line_ids.ids),
                ("account_id", "=", account.accrue_account_id.id),
            ]
            results = MoveLine.read_group(
                criteria, ["account_id", "debit", "credit"], ["account_id"], False
            )
            if len(results) > 0:
                account.write(
                    {
                        "debit": results[0]["debit"],
                        "credit": results[0]["credit"],
                    }
                )

    @ssi_decorator.post_done_action()
    def _create_move(self):
        Move = self.env["account.move"]
        move = Move.with_context(check_move_validity=False).create(
            self._prepare_account_move()
        )
        for account in self.account_ids:
            account._create_move_line(move)
        self.write(
            {
                "move_id": move.id,
            }
        )
        move.action_post()
        for account in self.account_ids:
            account._reconcile_move_line()

    def _prepare_account_move(self):
        return {
            "name": self.name,
            "date": self.date,
            "journal_id": self.journal_id.id,
        }

    @ssi_decorator.post_cancel_action()
    def _20_cancel_move(self):
        self.ensure_one()

        if not self.move_id:
            return True

        for account in self.account_ids:
            account._unreconcile_move_line()

        move = self.move_id
        self.write(
            {
                "move_id": False,
            }
        )

        if move.state == "posted":
            move.button_cancel()

        move.with_context(force_delete=True).unlink()
