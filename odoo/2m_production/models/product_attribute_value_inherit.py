# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class ProductAttributeValueInherit(models.Model):
    _inherit = "product.attribute.value"

    is_dimension = fields.Boolean("Est une dimension", related='attribute_id.is_dimension')

    length = fields.Float("Longueur")
    height = fields.Float("Hauteur")
    width = fields.Float("Largeur")
    dimensional_uom_id = fields.Many2one(
        "uom.uom",
        "Unité de mesure",
        domain=lambda self: self._get_dimension_uom_domain(),
        help="UoM for length, height, width",
        default=lambda self: self.env.ref("uom.product_uom_cm"))

    @api.model
    def _get_dimension_uom_domain(self):
        return [("category_id", "=", self.env.ref("uom.uom_categ_length").id)]

    # price_extra = fields.Float(
    #     string="Prix",
    #     default=0.0,
    #     digits='Product Price')
    #
    # application = fields.Selection(
    #     [("plank", "Prix de Planche"), ("product", "Prix de Produit")], string="Application sur", default="product"
    # )












