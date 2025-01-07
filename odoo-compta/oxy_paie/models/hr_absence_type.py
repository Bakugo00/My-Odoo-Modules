# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_absence_type(models.Model):
	_name = 'hr.absence.type'

	name = fields.Char(string="Désignation")
	code = fields.Char(string="Code")
	regle_id = fields.Many2one('hr.salary.rule', string="Règles salariales")


	_sql_constraints = [
		('code_type_abs', 'unique(code)', 'Le code doit être unique !'),
	]

	@api.model
	def create(self, data):
		res = super(hr_absence_type,self).create(data)
		#if not res.isRemu:
		regle_browse = self.env['hr.salary.rule'].search([('sequence','>=','100'),('sequence','<','200')])
		regle_list = []

		for reg in regle_browse:
			regle_list.append(reg.sequence)
		if (max(regle_list) + 1) > 199:
			sequence = 199
		else:
			sequence = max(regle_list) + 1

		if 'regle_id' not in data or not data['regle_id']:
			cat_id = self.env.ref('oxy_paie.MONTANT_ABSENCE')
			type = 'retenu'
			condition = "result = contract.schedule_pay == 'monthly' and worked_days." + str(res.code) + " or False"

			regle_data = {
				'name' : res.name,
				'code' : res.code,
				'sequence' : sequence,
				'category_id' : cat_id.id,
				'condition_select' : 'python',
				'condition_python' : condition,
				'amount_select' : 'percentage',
				'amount_percentage_base' : "worked_days." + str(res.code) + ".number_of_hours",
				'quantity' : 'contract.taux_horaire',
				'amount_percentage' : 100,
				'appears_on_payslip' : True,
				'type' : type,
			}

			regle_id_tmp = self.env[('hr.salary.rule')].create(regle_data)
			res.regle_id = regle_id_tmp.id
			struct_id = self.env.ref('oxy_paie.hr_payroll_salary_structure_heure')
			struct_id.rule_ids = [(4,regle_id_tmp.id)]
		#self.env[('hr.leave.type')].create({'name' : res.name,'allocation_type' : 'no',
		#	'absence_type' : res.id})
		return res


	def write(self, data):
		res = super(hr_absence_type,self).write(data)
		"""
		if 'name' in data :
			leave_type = self.env['hr.leave.type'].search([('absence_type','=',self.id)],limit=1)
			if leave_type:
				leave_type.name = self.name
			else:
				self.env[('hr.leave.type')].create({'name' : self.name,'allocation_type' : 'no',
					'absence_type' : self.id})"""
		if self.regle_id:
			#if not self.isRemu:
			if 'code' in data :
				self.regle_id.code = self.code
				self.regle_id.condition_python = "result = contract.schedule_pay == 'monthly' and worked_days." + str(self.code) + " or False"
				self.regle_id.amount_percentage_base = "worked_days." + str(self.code) + ".number_of_hours"
			if 'name' in data :
				self.regle_id.name = self.name
			#else:
				#if self.regle_id:
				#	self.regle_id.unlink()
		else:
			#if not self.isRemu:
			regle_browse = self.env['hr.salary.rule'].search([('sequence','>=','100'),('sequence','<','200')])
			regle_list = []
			for reg in regle_browse:
				regle_list.append(reg.sequence)
			if (max(regle_list) + 1) > 199:
				sequence = 199
			else:
				sequence = max(regle_list) + 1

			if 'regle_id' not in data or not data['regle_id']:
				cat_id = self.env.ref('oxy_paie.MONTANT_ABSENCE')
				type = 'retenu'
				condition = "result = contract.schedule_pay == 'monthly' and worked_days." + str(self.code) + " or False"
				regle_data={
					'name' : self.name,
					'code' : self.code,
					'sequence' : sequence,
					'category_id' : cat_id.id,
					'condition_select' : 'python',
					'condition_python' : condition,
					'amount_select' : 'percentage',
					'amount_percentage_base' : "worked_days." + str(self.code) + ".number_of_hours",
					'quantity' : 'contract.taux_horaire',
					'amount_percentage' : 100,
					'appears_on_payslip' : True,
					'type' : type,
					}

				regle_id_tmp = self.env[('hr.salary.rule')].create(regle_data)
				self.regle_id = regle_id_tmp.id
				struct_id = self.env.ref('oxy_paie.hr_payroll_salary_structure_heure')
				struct_id.rule_ids = [(4,regle_id_tmp.id)]
		return res

	def unlink(self):
		for rec in self:
			if rec.regle_id:
				rec.regle_id.unlink()
			#leave_id = self.env['hr.leave.type'].search([('absence_type','=',rec.id)])
			#if leave_id:
			#	leave_id.unlink()
		return super(hr_absence_type,self).unlink()

	def name_get(self):
		result = []
		for rec in self:
			name, code = rec.name, rec.code
			if code:
				name = '[%s] %s' % (code, name)
			result.append((rec.id, name))
		return result