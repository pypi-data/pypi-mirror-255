# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RevenueRecognitionFullTypeAccount(models.Model):
    _name = "revenue_recognition_full_type_account"
    _description = "Revenue Recognition (Full) Type Account Mapping"

    type_id = fields.Many2one(
        string="Type",
        comodel_name="revenue_recognition_full_type",
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
