from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Payment(models.Model):
    _inherit = 'account.payment'

    sale_order_ids = fields.Many2many('sale.order', string='Devis')

    @api.onchange('sale_order_ids')
    def _onchange_sale_order(self):
        if self.sale_order_ids:
            partner_id = set(order.partner_id for order in self.sale_order_ids)
            is_same_partner = len(partner_id) == 1
            if is_same_partner:
                self.amount = sum(self.sale_order_ids.mapped('amount_untaxed')) if self.sale_order_ids else 0
                self.partner_id = self.sale_order_ids[0].partner_id.id
            else:
                raise ValidationError(_("Il faut sélectionner des Devis de le même client !"))

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [
        (
            'check_accountable_required_fields',
             "CHECK(COALESCE(display_type IN ('line_section', 'line_note','line_composed_product'), 'f') OR account_id IS NOT NULL)",
             "Missing required account on accountable invoice line."
        ),
    ]

    display_type = fields.Selection(selection_add=[('line_composed_product', 'Article Composé')])
    new_quantity = fields.Float('Quantité Unitaire',required=True, default=1)
    new_price_unit = fields.Float('Prix unitaire')
        