# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"


    payment_method = fields.Selection([
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
        ('espece', 'Espèces')],
        string='Méthode de paiement', default='', tracking=True)
    
    amount_stamp = fields.Monetary(string="Montant Timbre", compute='_compute_amounts', store=True, default=0)

    

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total','payment_method')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        #stamp = self.env.ref("ep_stamp_tax.tva_stamp1") # TODO: we could hard code it!
        for order in self:
            super(SaleOrderInherit, order)._compute_amounts()
            if order.payment_method == 'espece':
                amount_stamp = order.amount_total * 1 / 100
                order.amount_stamp = amount_stamp
                order.amount_total = order.amount_total + amount_stamp
            else:
                order.amount_stamp = 0.0



    def _prepare_invoice(self):
        res = super(SaleOrderInherit, self)._prepare_invoice()


        res.update({
            'payment_method': self.payment_method,
        })
        return res
