# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _

class MissionEmployee(models.Model):
    _inherit = 'hr.employee'

    in_mission = fields.Boolean(string="En mission ?",default=False)
    start_date = fields.Date(string='Date de début')
    end_date = fields.Date(string='Date de fin')