
from odoo import api, fields, models, _, tools


class CompanyType(models.Model):
    _name = "company.type"
    _description = "Type d'entreprise"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    active = fields.Boolean(default=True)

