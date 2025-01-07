from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ActivityResult(models.Model):
    _name = "activity.result.category"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True,tracking=True)

    result_ids = fields.One2many(comodel_name="activity.result", inverse_name="categ_id",
                                 string="Résultats d'activités",tracking=True)

    type_ids = fields.Many2many('mail.activity.type', 'class_type_result_category', 'activity_result_category_id',
                                'mail_activity_type_id', string="Type d'activités",tracking=True)

    active = fields.Boolean(default=True)

    # @api.onchange('result_ids')
    # def get_type_ids(self):
    #     for category in self:
    #         for result in category.result_ids:
    #             print(result.type_ids)
    #             category.update({'type_ids': [(6, 0, result.type_ids)]})

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            result.append((record.id, name))
        return result

