# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class ProductTemplateAttributeLineInherit(models.Model):
    _inherit = "product.template.attribute.line"

    template_value_id = fields.Many2one('product.template.attribute.value', string="Valeur",
                                        domain="[('attribute_id', '=', attribute_id)]")

    # product_tmpl_id = fields.Many2one('product.template', related='template_value_id.product_tmpl_id')

    price_extra = fields.Float(related='template_value_id.price_extra', string="Prix")

    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=False, index=True)

    @api.constrains('active', 'value_ids', 'attribute_id')
    def _check_valid_values(self):
        for ptal in self:
            # if ptal.active and not ptal.value_ids:
            #     raise ValidationError(
            #         _("The attribute %s must have at least one value for the product %s.") %
            #         (ptal.attribute_id.display_name, ptal.product_tmpl_id.display_name)
            #     )
            for pav in ptal.value_ids:
                if pav.attribute_id != ptal.attribute_id:
                    raise ValidationError(
                        _("On the product %s you cannot associate the value %s with the attribute %s because they do not match.") %
                        (ptal.product_tmpl_id.display_name, pav.display_name, ptal.attribute_id.display_name)
                    )
        return True

