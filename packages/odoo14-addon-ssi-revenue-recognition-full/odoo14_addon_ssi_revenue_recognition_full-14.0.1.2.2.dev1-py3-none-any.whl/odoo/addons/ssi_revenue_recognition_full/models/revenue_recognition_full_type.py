# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RevenueRecognitionFullType(models.Model):
    _name = "revenue_recognition_full_type"
    _inherit = ["mixin.master_data"]
    _description = "Revenue Recognition (Full) Type"

    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
    )
    account_ids = fields.One2many(
        string="Account Mappings",
        comodel_name="revenue_recognition_full_type_account",
        inverse_name="type_id",
    )
