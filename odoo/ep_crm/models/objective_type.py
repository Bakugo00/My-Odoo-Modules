
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ObjectiveType(models.Model):
    _name = "objective.type"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', tracking=True)

    active = fields.Boolean(default=True)

    type = fields.Selection([('turnover', "Montant du chiffre d'affaires"),
                             ('sale_order_amount', 'Montant des bons de commande'),
                             ('payment_amount', 'Montant de recouvrement'),
                             ('sale_order_count', 'Nombre de devis'),
                             ('appointment_count', 'Nombre de rendez-vous'),
                             ], string='Type', tracking=True)

    objective_ids = fields.One2many(comodel_name='objective', inverse_name='type_id', string="Objectives")


