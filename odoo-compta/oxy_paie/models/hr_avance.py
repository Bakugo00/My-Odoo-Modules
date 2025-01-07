# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class hr_avance(models.Model):
	_name = "hr.avance"

	employee_id = fields.Many2one('hr.employee',string="Employé")
	decription = fields.Text('Description')
	date = fields.Date('Date',default=lambda self : datetime.now())
	amount = fields.Monetary('Montant')
	currency_id = fields.Many2one('res.currency',default=lambda self : self.env.user.company_id.currency_id)