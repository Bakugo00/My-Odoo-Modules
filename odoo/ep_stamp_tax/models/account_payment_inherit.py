# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools



class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    
    payment_method = fields.Selection([
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('espece', 'Espèce')],
        string='Méthode de paiement', default='virement', required=True, tracking=True)
    bank_check_number = fields.Char("Numéro de chèque")






