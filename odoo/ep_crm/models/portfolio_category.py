
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class PortfolioCategory(models.Model):
    _name = "portfolio.category"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)

    active = fields.Boolean(default=True)

    portfolio_ids = fields.One2many(comodel_name='portfolio', inverse_name='categ_id', string="Portefeuilles")

    company_ids = fields.Many2many('res.company', string='Companies')