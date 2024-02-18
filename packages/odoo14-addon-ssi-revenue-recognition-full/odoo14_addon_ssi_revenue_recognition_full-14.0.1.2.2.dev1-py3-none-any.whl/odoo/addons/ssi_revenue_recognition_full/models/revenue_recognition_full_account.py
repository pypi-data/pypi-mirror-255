# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RevenueRecognitionFullAccount(models.Model):
    _name = "revenue_recognition_full_account"
    _description = "Revenue Recognition (Full) Account Mapping"

    recognition_id = fields.Many2one(
        string="# Recognition",
        comodel_name="revenue_recognition_full",
        required=True,
        ondelete="cascade",
    )
    direction = fields.Selection(
        string="Direction",
        selection=[("revenue", "Revenue"), ("cost", "Cost")],
        required=True,
        default="revenue",
    )
    accrue_account_id = fields.Many2one(
        string="Accrue Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
    )
    account_id = fields.Many2one(
        string="Account",
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

    def _create_move_line(self, move):
        MoveLine = self.env["account.move.line"]
        debit_ml = MoveLine.with_context(check_move_validity=False).create(
            self._prepare_debit_move_line(move)
        )
        credit_ml = MoveLine.with_context(check_move_validity=False).create(
            self._prepare_credit_move_line(move)
        )
        self.write(
            {
                "debit_move_line_id": debit_ml.id,
                "credit_move_line_id": credit_ml.id,
            }
        )

    def _reconcile_move_line(self):
        self.ensure_one()
        if self.direction == "revenue":
            lines = self.debit_move_line_id
        else:
            lines = self.credit_move_line_id

        MoveLines = self.env["account.move.line"]
        criteria = [
            ("id", "in", self.recognition_id.move_line_ids.ids),
            ("account_id", "=", self.accrue_account_id.id),
        ]
        origin_lines = MoveLines.search(criteria)
        lines = lines + origin_lines
        lines.reconcile()

    def _unreconcile_move_line(self):
        if self.direction == "revenue":
            lines = self.debit_move_line_id
        else:
            lines = self.credit_move_line_id

        lines.remove_move_reconcile()

    def _prepare_credit_move_line(self, move):
        self.ensure_one()
        amount = abs(self.debit - self.credit)
        if self.direction == "revenue":
            account = self.account_id
        else:
            account = self.accrue_account_id

        result = self._prepare_move_line(move, account, 0.0, amount)
        return result

    def _prepare_debit_move_line(self, move):
        self.ensure_one()
        amount = abs(self.debit - self.credit)
        if self.direction == "cost":
            account = self.account_id
        else:
            account = self.accrue_account_id
        result = self._prepare_move_line(move, account, amount, 0.0)
        return result

    def _prepare_move_line(self, move, account, debit, credit):
        name = "Revenue recognation %s" % (self.recognition_id.name)
        recognition = self.recognition_id
        return {
            "move_id": move.id,
            "name": name,
            "account_id": account.id,
            "analytic_account_id": recognition.analytic_account_id.id,
            "debit": debit,
            "credit": credit,
        }
