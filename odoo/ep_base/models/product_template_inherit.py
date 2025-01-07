
import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    # Add this field to differentiate confirmed product from not-confirmed product
    confirmed_type = fields.Selection(
        selection=[("confirmed", "Confirmé"), ("not-confirmed", "Non Confirmé")],
        string="Etat d'article",
        default="not-confirmed",
        required=True,
        help="Les produits seront confirmés automatiquement aprés leurs ventes"
    )

    # Add store=True to standard_price
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user", store=True,
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the last unit that left the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
    
    state = fields.Selection(
        selection=[
            ('draft', "Brouillon"),
            ('confirmed', "Confirmé"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    # def _set_standard_price(self):
    #     for template in self:
    #         if len(template.product_variant_ids) == 1:
    #             template.product_variant_ids.standard_price = template.standard_price
    #
    # def _search_standard_price(self, operator, value):
    #     products = self.env['product.product'].search([('standard_price', operator, value)], limit=None)
    #     return [('id', 'in', products.mapped('product_tmpl_id').ids)]
    #
    # @api.depends_context('company')
    # @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    # def _compute_standard_price(self):
    #     # Depends on force_company context because standard_price is company_dependent
    #     # on the product_product
    #     unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
    #     for template in unique_variants:
    #         template.standard_price = template.product_variant_ids.standard_price
    #     for template in (self - unique_variants):
    #         template.standard_price = 0.0

    def action_confirm(self):
        for product_template in self:
            product_template.write({'state': 'confirmed'})
        return True

    def action_cancel(self):
        for product_template in self:
            product_template.write({'state': 'draft'})
        return True

