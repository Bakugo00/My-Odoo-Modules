# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_method = fields.Selection([
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('espece', 'Espèce')],
        string='Méthode de paiement', default='virement', required=True, tracking=True)

    bank_check_number = fields.Char("Numéro de chèque")


    def _create_payment_vals_from_wizard(self,batch_result):
        res = super(AccountPaymentRegisterInherit,self)._create_payment_vals_from_wizard(batch_result)
        res.update({
            'payment_method': self.payment_method,
            'bank_check_number': self.bank_check_number,
        })
        return res
