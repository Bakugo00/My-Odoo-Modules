# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools



class SaleOrderInherit(models.Model):
    _inherit = "sale.order"


    discount_type = fields.Selection([('percent', 'Pourcentage'), ('amount', 'Montant')], string='Type de remise',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, store=True)

    discount_rate = fields.Float('Taux de remise',
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, store=True)

    amount_discount = fields.Monetary(string='Montant de remise Globale', store=True, readonly=True, compute='_compute_amounts',
                                      track_visibility='always')


    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total','discount_type','discount_rate')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            super(SaleOrderInherit, order)._compute_amounts()
            # Add global discount calculation
            total = 0.0
            if order.discount_type == 'percent':
                for line in order.order_line:
                    total += line.price_subtotal
                order.amount_discount =total * (order.discount_rate / 100.0)
            elif order.discount_type == 'amount':
                order.amount_discount = order.discount_rate
            else:
                order.amount_discount =  0.0

            order.amount_untaxed = order.amount_untaxed - order.amount_discount
            order.amount_total = order.amount_untaxed + order.amount_tax 
            order.amount_text = order.currency_id and order.currency_id.amount_to_text(order.amount_total ) or ''

    def _prepare_invoice(self):
        res = super(SaleOrderInherit, self)._prepare_invoice()


        res.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
        })
        return res
