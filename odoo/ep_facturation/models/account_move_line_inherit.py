from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from num2words import num2words


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "date desc, move_name desc, id"

    # @api.depends('name')
    # def _get_compute_istimbre(self):
    #     for rec in self:
    #         if rec.name == 'Timbre':
    #             rec.istimbre = True
    #         else:
    #             rec.istimbre = False

    # istimbre = fields.Boolean(compute="_get_compute_istimbre", store=True)

    discount = fields.Float(string='Remise (%)', default=0.0)



