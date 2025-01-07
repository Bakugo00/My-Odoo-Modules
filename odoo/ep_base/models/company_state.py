
from odoo import api, fields, models, _, tools


class CompanyState(models.Model):
    _name = "company.state"
    _description = "Etat d'entreprise"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    active = fields.Boolean(default=True)

