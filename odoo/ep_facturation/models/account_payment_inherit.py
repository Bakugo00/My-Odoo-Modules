# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from num2words import num2words


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    # Redefine this fields to add store=True and tracking=True
    date = fields.Datetime('Date', store=True, tracking=True)
    ref = fields.Char(store=True, tracking=True)
    old_id = fields.Integer('old_id')
    # payment_method = fields.Selection([
    #     ('virement', 'Virement'),
    #     ('cheque', 'Chèque'),
    #     ('espece', 'Espèce')],
    #     string='Méthode de paiement', default='virement', required=True, tracking=True)

    # bank_check_number = fields.Char("Numéro de chèque")






