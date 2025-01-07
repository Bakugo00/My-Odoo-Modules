
from odoo import api, fields, models, _, tools


class RecoveryStep(models.Model):
    _name = "recovery.step"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Text(string='Description', required=True, tracking=True)
    active = fields.Boolean(default=True)

