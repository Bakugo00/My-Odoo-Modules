
from odoo import api, fields, models, _, tools


class Email(models.Model):
    _name = "email"
    _description = "Email"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Email', tracking=True)
    partner_id = fields.Many2one('res.partner', "Partenaire", tracking=True)
    default_email = fields.Boolean("Par défault", default=False, tracking=True)
    active = fields.Boolean(default=True)


