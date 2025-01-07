
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    customer_contract_id = fields.Many2one("customer.contract", string="Réf Contrat client", tracking=True)
    supplier_contract_id = fields.Many2one("supplier.contract", string="Réf Contrat fournisseur", tracking=True)

    @api.onchange('customer_contract_id')
    def _onchange_customer_contract_id(self):
        if not self.customer_contract_id:
            return

        self = self.with_company(self.company_id)
        customer_contract = self.customer_contract_id
        if self.partner_id:
            partner = self.partner_id
        # else:
        #     partner = requisition.vendor_id
        # payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        # self.partner_id = partner.id
        # self.fiscal_position_id = fpos.id
        # self.payment_term_id = payment_term.id,
        self.company_id = customer_contract.company_id.id
        self.currency_id = customer_contract.currency_id.id
        if not self.origin or customer_contract.name not in self.origin.split(', '):
            if self.origin:
                if customer_contract.name:
                    self.origin = self.origin + ', ' + customer_contract.name
            else:
                self.origin = customer_contract.name
        self.note = customer_contract.note
        self.date_order = fields.Datetime.now()

        # if requisition.type_id.line_copy != 'copy':
        #     return

        # Create SO lines if necessary
        order_lines = []
        for line in customer_contract.contract_line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang or self.env.user.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == customer_contract.company_id)).ids
            # print("taxes_ids 1 ", taxes_ids)
            # Compute quantity and price_unit
            # if line.product_uom_id != line.product_id.uom_po_id:
            #     product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
            #     price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            # else:
            product_uom_qty = line.product_uom_qty
            price_unit = line.price_unit
            # taxes_ids = [(4, line.taxes_ids.ids)]
            # taxes_ids.append(line.taxes_ids.ids)
            # taxes_ids = [(4, line.taxes_ids)]
            taxes_ids = line.taxes_ids
            print("taxes_ids", [(4, line.taxes_ids.ids)])
            print("taxes_ids 2", taxes_ids)

            # 'invoice_line_ids': [(0, 0, {
            #     'tax_ids': [(6, 0, so_line.tax_id.ids)],

            # Create SO line
            order_line_values = line._prepare_sale_order_line(
                name=name, product_uom_qty=product_uom_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

    @api.constrains('amount_untaxed')
    def check_amount_untaxed_of_sale_customer_contract(self):
        for rec in self:
            if rec.customer_contract_id:
                domain_so = [('customer_contract_id', '=', rec.customer_contract_id.id)]
                domain_cc = [('id', '=', rec.customer_contract_id.id)]
                total_so = sum(self.env['sale.order'].search(domain_so).mapped('amount_untaxed'))
                total_cc = sum(self.env['customer.contract'].search(domain_cc).mapped('amount_untaxed'))

                if total_so > total_cc:
                    raise ValidationError(_('Vous avez dépassé le montant du contrat'))
                    # raise ValidationError(_('Vous ne pouvez pas créer ce devis pour ce contrat !!'
                    #                         'les montants des devis ( %s )'
                    #                         'dépasse le montant du contrat ( %s )',
                    #                          total_so,total_cc))
