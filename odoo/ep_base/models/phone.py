
from odoo import api, fields, models, _, tools


class Phone(models.Model):
    _name = "phone"
    _description = "Téléphone"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Télephone', tracking=True)
    partner_id = fields.Many2one('res.partner', "Partenaire", tracking=True)
    default_phone = fields.Boolean("Par défault", default=False, tracking=True)
    active = fields.Boolean(default=True)


