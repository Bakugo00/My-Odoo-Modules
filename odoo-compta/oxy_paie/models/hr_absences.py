# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_absences(models.Model):
	_name = 'hr.absences'

	employee_id = fields.Many2one('hr.employee', string="Employé")
	absence_type = fields.Many2one('hr.absence.type', string="Type d'absence")
	date = fields.Date(string="Date")
	qte = fields.Float(string="Qté en heures")