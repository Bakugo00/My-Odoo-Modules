
from odoo import api, fields, models, _, tools


class CompanyStatus(models.Model):
    _name = "company.status"
    _description = "Statut d'entreprise"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    active = fields.Boolean(default=True)

