from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # mrp_production_count = fields.Integer(
    #     "Count of MO generated",
    #     compute='_compute_mrp_production_count',
    #     groups='mrp.group_mrp_user', store=True)

    delivery_method = fields.Many2one('delivery.method', string='Moyen de livraison')
    payment_for_sale_count = fields.Integer(
        "Nombres des paiements",
        compute='_compute_payments_for_sale_count',
        groups='account.group_account_invoice', default=0)

    def _compute_payments_for_sale_count(self):
        for sale in self:
            payment_for_sale_count = self.env['account.payment'].search_count([('sale_order_ids', 'in', sale.ids)])
            sale.payment_for_sale_count = payment_for_sale_count

    def action_view_payments_in_sale(self):
        self.ensure_one()
        payment_ids = self.env['account.payment'].search([('sale_order_ids', 'in', self.ids)]).ids
        action = {
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
        }
        if len(payment_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payment_ids[0],
            })
        else:
            action.update({
                'name': _("Les paiements effectués pour %s", self.name),
                # 'domain': [('id', 'in', payment_ids)],
                'domain': [('id', 'in', payment_ids)],
                'view_mode': 'tree,form',
            })
        return action

    mrp_production_in_sale_count = fields.Integer(
        "Count of MO generated",
        compute='_compute_mrp_production_in_sale_count',
        groups='mrp.group_mrp_user', default=0)

    def _compute_mrp_production_in_sale_count(self):
        for sale in self:
            mrp_production_in_sale_count = self.env['mrp.production'].search_count([('sale_id', '=', sale.id)])
            sale.mrp_production_in_sale_count = mrp_production_in_sale_count
            sale.mrp_production_count = 0

    def action_view_mrp_production_in_sale(self):
        self.ensure_one()
        # mrp_production_ids = self.env['mrp.production'].search([('procurement_group_id.sale_id', '=', self.id)]).ids
        mrp_production_ids = self.env['mrp.production'].search([('sale_id', '=', self.id)]).ids
        # print('mrp_production_ids', mrp_production_ids)
        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
        }
        if len(mrp_production_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': mrp_production_ids[0],
            })
        else:
            action.update({
                'name': _("Ordre de fabrication généré par %s", self.name),
                # 'domain': [('id', 'in', mrp_production_ids)],
                'domain': [('sale_id', '=', self.id)],
                'view_mode': 'tree,form',
                'context':{'search_default_parent_product': True}
            })
        return action

    customer_type = fields.Selection(related='partner_id.customer_type')

    def action_confirm(self):
        #add this dev to modify the mrp_bom of the article in order to correct stock consommation
        for order in self.sudo():
            for line in order.order_line:
                # line.product_id.bom_ids = [(5, 0, 0)]
                #product_id = 
                if line.product_id.bom_ids:
                    line.product_id.bom_ids[0].product_qty = line.product_uom_qty
                    line.product_id.bom_ids[0].bom_line_ids.product_id = line.product_to_consume.product_variant_ids[0] #plank_id.product_variant_ids[0].id if line.plank_id else line.roleau_id.product_variant_ids[0].id
                    line.product_id.bom_ids[0].bom_line_ids.product_qty = int(line.product_uom_qty/line.nombre_de_pose) + 1
                else:
                    bom_values = {'product_tmpl_id':line.product_template_id.id,'product_qty':line.nombre_de_pose,
                                 'bom_line_ids':[(0,0,{'product_id':line.product_to_consume.id,'product_qty':1,})]}
                    self.env['mrp.bom'].sudo().create(bom_values)
        res = super(SaleOrderInherit, self).action_confirm()

        if not self.commitment_date:
            raise ValidationError(_('Veuillez préciser la date de livraison'))
        if not self.delivery_method:
            raise ValidationError(_('Veuillez préciser la méthode de livraison'))
        if not self.commitment_date and self.delivery_method:
            raise ValidationError(_('Veuillez préciser la date et la méthode de livraison'))

        return res

    doc_ids = fields.One2many('document', 'sale_order_id', string='Documents')

    #Compute the total quantity for composed product
    @api.onchange('order_line')
    def _onchange_new_qunatity(self):
        for line in self.order_line:
            if line.display_type != 'line_composed_product':
                lines = line.order_id.order_line.filtered(lambda so_line : so_line.sequence < line.sequence and so_line.display_type =='line_composed_product')
                if lines:
                    composed_product_line = max(lines, key=lambda line: line.sequence)
                    qty = line.new_quantité * composed_product_line.new_quantité
                    line.product_uom_qty = qty
                else:
                    line.product_uom_qty = line.new_quantité
            else:
                for l in sorted(line.order_id.order_line, key=lambda ln:ln.sequence):
                    if l.sequence > line.sequence:
                        if l.display_type == 'line_composed_product':
                            break
                        else:
                            qty = line.new_quantité * l.new_quantité
                            l.product_uom_qty = qty

    # Comment this function now -> It will be added with invoicing module
    # @api.onchange('partner_id', 'amount_total')
    # @api.constrains('partner_id', 'amount_total')
    # def check_amount(self):
    #     for sale_order in self:
    #         amount = fields.Float(digits=(12, 2), default=0)
    #         if sale_order.partner_id and sale_order.order_line:
    #             amount_total = sale_order.amount_total
    #             total_unpaid_invoiced = sale_order.partner_id.total_unpaid_invoiced
    #             unpaid_amount_authorized = sale_order.partner_id.unpaid_amount_authorized
    #             amount = amount_total + total_unpaid_invoiced
    #
    #             if amount > unpaid_amount_authorized:
    #                 if self.env.user.has_group('2m_production.group_sale_create_all_quotations'):
    #                     # Display a warning message
    #                     message = _('Le montant du '
    #                                 'devis ( %s ) + le montant Impayé ( %s ) = ( %s ) '
    #                                 'dépasse le montant impayé autorisé ( %s )',
    #                                 amount_total, total_unpaid_invoiced, amount, unpaid_amount_authorized)
    #
    #                     warning_mess = {
    #                         'title': _('Attention !'),
    #                         'message': message
    #                     }
    #                     return {'warning': warning_mess}
    #                 else:
    #                     # Raise a constrains
    #                     raise ValidationError(_('Vous ne pouvez pas créer ce devis pour ce client !! le montant du '
    #                                             'devis ( %s ) + le montant Impayé ( %s ) = ( %s ) '
    #                                             'dépasse le montant impayé autorisé ( %s )',
    #                                             amount_total, total_unpaid_invoiced, amount, unpaid_amount_authorized))
    def check_manufacturing_progression(self):
        man_orders = self.env['mrp.production'].search([('sale_id','=',self.id)])
        res = False
        if man_orders:
            done = 0
            for mn_order in man_orders:
                if mn_order.state == 'done':
                    done +=1
            progression = done* 100 / len(man_orders)
            res = "Etat d'avancement est: %s " % (progression)+ "%"
        return res

    def name_get(self):
        if self._context.get('display_progression'):
            res = []
            for order in self:
                name = order.name
                progression = order.check_manufacturing_progression()
                if progression:
                    name = '%s - %s' % (name,progression)
                res.append((order.id, name))
            return res
        return super(SaleOrderInherit, self).name_get()
    
    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line:
            #get line_composed_product line as invoiceable line
            if line.display_type == 'line_section' or line.display_type == 'line_composed_product':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)

        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)
