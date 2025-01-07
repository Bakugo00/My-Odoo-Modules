# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    partner_id = fields.Many2one('res.partner', string='Client', domain=[('company_type','=','company')])
    end_trial_prd_date = fields.Date("Date de fin de période d'éssai ")


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    in_mission = fields.Boolean("in mission")
    start_date = fields.Date()
    end_date = fields.Date()