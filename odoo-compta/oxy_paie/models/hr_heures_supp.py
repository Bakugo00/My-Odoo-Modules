# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from datetime import datetime

class hr_heures_supp(models.Model):
	_name = 'hr.heures.supp'

	employee_id = fields.Many2one('hr.employee', string="Employé")
	type_id = fields.Many2one('hr.heures.supp.type', string="Type heures supplémentaire")
	date = fields.Date(string="Date", default=lambda self:datetime.now())
	qte = fields.Float(string="Qté en heures")