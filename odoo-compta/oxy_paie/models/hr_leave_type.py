from odoo import models, api, fields

class hr_leave_type(models.Model):
	_inherit = 'hr.leave.type'

	absence_type = fields.Many2one('hr.absence.type','Type absence')