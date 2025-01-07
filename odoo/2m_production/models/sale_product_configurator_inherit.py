
from odoo import api, fields, models


class SaleProductConfiguratorInherit(models.TransientModel):
    # _name = "sale.product.configurator.inherit"
    _inherit = "sale.product.configurator"

    @api.model
    def _get_dimension_uom_domain(self):
        return [("category_id", "=", self.env.ref("uom.uom_categ_length").id)]

    product_length = fields.Float("Longueur")
    product_height = fields.Float("Hauteur")
    product_width = fields.Float("Largeur")

    dimensional_uom_id = fields.Many2one(
        "uom.uom",
        "Unité de mesure",
        domain=lambda self: self._get_dimension_uom_domain(),
        help="UoM for length, height, width",
        readonly=False)

    @api.model
    def default_get(self, fields_list):
        # Put default salesman in participant list
        res = super(SaleProductConfiguratorInherit, self).default_get(fields_list)
        product_template_id = self.env['product.template'].browse(res.get('product_template_id'))

        res.update({
            'product_length': product_template_id.product_length,
            'product_height': product_template_id.product_height,
            'product_width': product_template_id.product_width,
            'dimensional_uom_id': product_template_id.dimensional_uom_id,
        })
        return res


