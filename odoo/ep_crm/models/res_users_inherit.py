
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ResUsersInherit(models.Model):
    _inherit = "res.users"

    portfolio_ids = fields.Many2many('portfolio', 'class_portfolio_users',   'res_users_id', 'portfolio_id', string="Portefeuilles")
    # partner_ids = fields.Many2many('res.partner', 'class_res_users_res_partner', 'res_users_id','res_partner_id', string="Entreprises")

    # sale_order_ids = fields.One2many(comodel_name='sale.order', inverse_name='user_id')
    # attendees_ids = fields.One2many(comodel_name='sale.attendees', inverse_name='user_id')
