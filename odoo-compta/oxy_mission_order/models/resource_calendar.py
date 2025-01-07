# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class resource_calendar(models.Model):
	_inherit = 'resource.calendar'

	@api.depends('attendance_ids')
	def get_heure(self):
		for line in self:
			if line .attendance_ids:
				s_ids = self.env['resource.calendar.attendance'].search([('calendar_id','=',line.id),('dayofweek','=',line.attendance_ids[0].dayofweek)])
				min = s_ids[0].hour_from
				max = s_ids[0].hour_to
				for res in s_ids:
					if res.hour_from < min:
						min = res.hour_from
					if res.hour_to > max:
						max = res.hour_to
				line.heure_entre = min
				line.heure_sortie = max


	heure_entre = fields.Float('Heure d\'entrée',compute='get_heure',store=True)
	heure_sortie = fields.Float('Heure sortie',compute='get_heure',store=True)