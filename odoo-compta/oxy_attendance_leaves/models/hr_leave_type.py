# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class hr_leave_type(models.Model):
	_inherit = "hr.leave.type"

	include_dayoff = fields.Boolean('Inclus les week-end')