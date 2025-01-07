from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError




class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    discount_type = fields.Selection([('percent', 'Pourcentage'), ('amount', 'Montant')], string='Type de remise'
                                     )

    discount_rate = fields.Float('Taux de remise', digits=(16, 2))

    amount_discount = fields.Monetary(string='Montant de remise globale', store=True,
                                      track_visibility='always',compute='_compute_amount_discount')

    @api.depends('invoice_line_ids.price_unit','invoice_line_ids.is_discount_line')
    def _compute_amount_discount(self):
        for move in self:
            amount = -1 * sum(move.invoice_line_ids.filtered(lambda l:l.is_discount_line).mapped('price_unit'))
            move.amount_discount = amount
    
    def _create_global_discount_line(self,discount_line=False):
        self.ensure_one()
        if self.discount_type == 'amount':
            discount_amount =  self.discount_rate
        elif self.discount_type == 'percent':
            no_discount_lines = self.invoice_line_ids.filtered(lambda line: line.name != 'Remise Globale')
            if no_discount_lines :
                total = 0 
                for line in no_discount_lines:
                    total += line.price_subtotal
                discount_amount = abs(total * (self.discount_rate / 100.0))
            else:
                0.0
        else:
            discount_amount =  0.0

        if discount_line:
            discount_line.with_context({'approve_discount':True}).price_unit = -discount_amount
        else:
            if discount_amount != 0.0:
                vals = {
                    'name': 'Remise Globale',
                    'is_discount_line':True,
                    'quantity': 1,  
                    'price_unit': -discount_amount,
                    'tax_ids': False,
                    'move_id': self.id,
                }
                self.env['account.move.line'].with_context({'approve_discount':True}).create(vals)


    def action_discount(self):
        if not self.discount_rate or not self.discount_type:
            raise ValidationError(_('Veuillez préciser le type et le taux de remise !!')) 
        discount_line = self.invoice_line_ids.filtered(lambda line: line.name == 'Remise Globale')#.sudo().unlink()
        self._create_global_discount_line(discount_line)


    def write(self, vals):
        res = super(AccountMoveInherit, self).write(vals)
        for move in self:
            if 'discount_rate' in vals or 'discount_type' in vals :
                discount_line = move.invoice_line_ids.filtered(lambda line: line.name == 'Remise Globale')#.sudo().unlink()
                move._create_global_discount_line(discount_line)
        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        moves = super(AccountMoveInherit, self).create(vals_list)
        for move,vals in zip(moves,vals_list):
            if vals.get('discount_rate') or vals.get('discount_type'):
                discount_line = move.invoice_line_ids.filtered(lambda line: line.name == 'Remise Globale')
                move._create_global_discount_line(discount_line)
        return moves
  
class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    is_discount_line = fields.Boolean('Is discount line')

    def write(self, vals):
        for line in self:
            if line.is_discount_line and not self.env.context.get('approve_discount'):
                if 'product_id'  in vals or 'quantity' in vals or 'product_uom_id' in vals or 'price_unit'in vals or 'tax_ids'in vals or 'discount' in vals:
                    raise ValidationError(_('Vous ne pouvez pas modifier la ligne de remise manuellement'))
        return super().write(vals)
    

