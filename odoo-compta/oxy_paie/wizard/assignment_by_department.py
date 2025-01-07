# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class assignment_by_department(models.TransientModel):
	_name = 'assignment.by.department'

	department_id = fields.Many2one('hr.department','Département')
	rate = fields.Float(string="Taux/Montant")

	def enregistrer(self):
		dicts = {}
		hr_primes = self.env['hr.primes'].browse(self.env.context.get('active_id', []))
		if hr_primes.state != 'brouillon':
			raise UserError(('Vous ne pouvez pas faire des modification sur des primes validé!'))
		employee = self.env['hr.employee'].search([('department_id', '=', self.department_id.id),('non_actif', '=', False)])
		for emp in employee:
			dicts['employee_id'] = emp.id
			dicts['hr_primes_id'] = hr_primes.id
			dicts['taux_montant'] = self.rate
			self.env['hr.primes.lines'].create(dicts)
		return True