
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ActivityResult(models.Model):
    _name = "activity.result"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True,tracking=True)

    categ_id = fields.Many2one(string="Catégorie de résultat", comodel_name="activity.result.category",tracking=True)

    # type_ids = fields.Many2many('mail.activity.type', 'class_type_result', 'activity_result_id', 'mail_activity_type_id', string="Type d'activités",tracking=True)

    active = fields.Boolean(default=True)


