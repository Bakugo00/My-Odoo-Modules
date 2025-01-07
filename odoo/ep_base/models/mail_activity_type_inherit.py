# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class MailActivityTypeInherit(models.Model):
    _inherit = "mail.activity.type"

    # result_ids = fields.Many2many('activity.result', 'class_type_result', 'mail_activity_type_id', 'activity_result_id')

    result_category_ids = fields.Many2many('activity.result.category', 'class_type_result_category',
                                           'mail_activity_type_id', 'activity_result_category_id')
