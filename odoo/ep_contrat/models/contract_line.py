from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class ContractLine(models.Model):
    _name = 'contract.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = "name"

    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, tracking=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)

    supplier_contract_id = fields.Many2one('supplier.contract', string='Réf contrat fournisseur', ondelete='cascade', index=True, copy=False)
    customer_contract_id = fields.Many2one('customer.contract', string='Réf contrat client',ondelete='cascade', index=True, copy=False)
    description = fields.Text(string='Description', required=True)
    price_unit = fields.Float('Prix Unitaire', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    taxes_ids = fields.Many2many('account.tax', string='TVA', domain=['|', ('active', '=', False), ('active', '=', True)])

    product_id = fields.Many2one(
        'product.product', string='Produit', change_default=True, ondelete='restrict', required=True)  # Unrequired company
    # product_template_id = fields.Many2one(
    #     'product.template', string='Product Template',
    #     related="product_id.product_tmpl_id")
    product_uom_qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unité de mesure')

    discount = fields.Float(string='Remise (%)', digits='Discount', default=0.0)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'taxes_ids')
    def _compute_amount(self):
        """
        Compute the amounts of the contract line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_ids.compute_all(price, line.customer_contract_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.customer_contract_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.taxes_ids.invalidate_cache(['invoice_repartition_line_ids'], [line.taxes_ids.id])

    @api.onchange('product_id')
    def affect_description(self):
        for record in self:
            record.description = record.product_id.name

    def _prepare_sale_order_line(self, name, product_uom_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        customer_contract = self.customer_contract_id
        # if self.product_description_variants:
        #     name += '\n' + self.product_description_variants
        # if customer_contract.schedule_date:
        #     date_planned = datetime.combine(requisition.schedule_date, time.min)
        # else:
        #     date_planned = datetime.now()
        # print("taxes_ids.ids line", taxes_ids.ids)
        return {
            'name': name,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'product_uom_qty': product_uom_qty,
            'price_unit': price_unit,
            'tax_id': [(6, 0, taxes_ids.ids)],
            # 'tax_id': [(6, 0, taxes_ids)],
            # 'date_planned': date_planned,
            # 'account_analytic_id': self.account_analytic_id.id,
            # 'analytic_tag_ids': self.analytic_tag_ids.ids,
        }
