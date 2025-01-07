# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    category_policy = fields.Selection([
        ('buy', 'Acheter'),('manufacture','Produite')
    ], string='Cette Catégorie doit être:',required=True)
    dimension = fields.Selection([
        ('two', '2 Dimensions(X,Y)'),('one','Une Seule(X)')
    ], string='Dimension',required=True,default='two')
    categ_id = fields.Many2one('product.category', string='Catégorie à consommer')
    use_limit = fields.Boolean('Limiter le nombre de pose')
    limit = fields.Integer('Limite')