# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    address_home_id = fields.Many2one(
        'res.partner', 'Contact',
        help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=True,
        domain="[ ('company_type', '=', 'person')]" )

