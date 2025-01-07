# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class ProductAttributeInherit(models.Model):
    _inherit = "product.attribute"

    # application = fields.Selection(
    #     [("plank", "Prix de Planche"), ("product", "Prix de Produit")], string="Application sur", default="product"
    # )
    #
    # calculation_type = fields.Selection(
    #     [("addition", "Addition"), ("substraction","Soustraction"), ("multiplication","Multiplication"), ("division","Division")],
    #     string="Type de calcul", default="addition"
    # )
    #
    # step = fields.Selection(
    #     [("1", "Etape 1"), ("2", "Etape 2"), ("3", "Etape 3"), ("4", "Etape 4"), ("5", "Etape 5")],
    #     string="Etape", default="1"
    # )
    #
    # discount = fields.Boolean("Appliquer la remise")
    # change_price = fields.Boolean("Changer le prix")
    # price_extra = fields.Float(
    #     string="Prix",
    #     default=0.0,
    #     digits='Product Price')

    is_dimension = fields.Boolean("Est une dimension")

    display_type = fields.Selection([
        ('select', 'Select'),
        ('color', 'Color')], default='select', required=True, help="The display type used in the Product Configurator.")

    @api.model_create_multi
    def create(self, vals):
        res = super(ProductAttributeInherit, self).create(vals)
        attribute_id = self.env["product.attribute.value"].sudo().create({'name':'Sans','attribute_id':res.id})
        return res









