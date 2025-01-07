# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    old_id = fields.Integer('old_id')
    # payment_method = fields.Selection([
    #     ('virement', 'Virement'),
    #     ('cheque', 'Chèque'),
    #     ('espece', 'Espèce')],
    #     string='Méthode de paiement', default='virement', required=True, tracking=True)

    # bank_check_number = fields.Char("Numéro de chèque")
    # partner_bank_id = fields.Many2one(
    #     comodel_name='res.partner.bank',
    #     string="Recipient Bank Account",
    #     readonly=False,
    #     store=True,
    #     compute='_compute_partner_bank_id',
    #     domain="['|',('company_id', '=',False),('company_id','=',company_id),('partner_id','=',partner_id)]",
    # )

    # @api.depends("payment_method")
    # @api.onchange("payment_method")
    # def affect_journal_id(self):
    #     for rec in self:
    #         if rec.payment_method == "espece":
    #             rec.journal_id = self.env['account.journal'].search([('id', '=', 7)]).id
    #         else:
    #             rec.journal_id = self.env['account.journal'].search([('id', '=', 8)]).id

    def _create_payment_vals_from_wizard(self,batch_result):
        res = super(AccountPaymentRegisterInherit,self)._create_payment_vals_from_wizard(batch_result)
        res.update({
            'old_id': self.old_id,
        })
        return res
