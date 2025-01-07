# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_rappel(models.Model):
	_name = 'hr.rappel'

	rappel_type_id = fields.Many2one('hr.rappel.type', string="Types rappel")
	date = fields.Date(string="Date")
	employee_id = fields.Many2one('hr.employee', string="Employé")
	taux_montant = fields.Float(string='Montant')
	