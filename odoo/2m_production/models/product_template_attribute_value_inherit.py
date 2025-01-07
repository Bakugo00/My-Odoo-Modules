# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class ProductTemplateAttributeValueInherit(models.Model):
    _inherit = "product.template.attribute.value"

    application = fields.Selection(
        [("plank", "Prix de Planche"), ("product", "Prix de Produit")], string="Application sur", default="product"
    )
    #Redefine this methode to change the product description
    def _get_combination_name(self):
        """Exclude values from single value lines or from no_variant attributes."""
        ptavs = self._without_no_variant_attributes().with_prefetch(self._prefetch_ids)
        ptavs = ptavs._filter_single_value_lines().with_prefetch(self._prefetch_ids)
        name= '\n'
        for ptav in ptavs:
            if ptav.name != 'Sans':
                name +='    -'+ ptav.attribute_id.name +': '+ ptav.name+ '\n'
        return name








