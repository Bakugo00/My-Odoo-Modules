from odoo import fields, models, api


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    posted = fields.Boolean(default=False)
    old_move_id = fields.Integer()
    quotation_id = fields.Integer()
