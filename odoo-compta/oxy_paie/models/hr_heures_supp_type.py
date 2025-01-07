# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_heures_supp_type(models.Model):
	_name = 'hr.heures.supp.type'
	_order = "code"

	name = fields.Char(string="Désignation")
	code = fields.Char(string="Code")
	majoration = fields.Float('Majoration(%)')
	regle_id = fields.Many2one('hr.salary.rule', string="Règles salariales")


	_sql_constraints = [
		('code_type_abs', 'unique(code)', 'le code doit etre unique !'),
	]


	@api.model
	def create(self, data):
		res = super(hr_heures_supp_type,self).create(data)
		if 'regle_id' not in data or not data['regle_id']:
			cat_id = self.env.ref('oxy_paie.HSUP_DECL')
			type = 'gain'
			condition = "result = contract.schedule_pay == 'monthly' and hsup." + str(res.code) + " or False"
			regle_data = {
				'name' : res.name,
				'code' : res.code,
				'sequence' : 402,
				'category_id' : cat_id.id,
				'condition_select' : 'python',
				'condition_python' : condition,
				'amount_select' : 'percentage',
				'amount_percentage_base' : "hsup." + str(res.code) + ".qty",
				'quantity' : 'contract.taux_horaire',
				'amount_percentage' : 100 + res.majoration,
				'appears_on_payslip' : True,
				'type' : type,
			}
			regle_id_tmp = self.env[('hr.salary.rule')].create(regle_data)
			res.regle_id = regle_id_tmp.id
			struct_id = self.env.ref('oxy_paie.hr_payroll_salary_structure_heure')
			struct_id.rule_ids = [(4,regle_id_tmp.id)]
		return res

	def write(self, data):
		res = super(hr_heures_supp_type,self).write(data)
		if self.regle_id:
			if 'code' in data :
				self.regle_id.code = self.code
				self.regle_id.condition_python = "result = contract.schedule_pay == 'monthly' and hsup." + str(self.code) + " or False"
				self.regle_id.amount_percentage_base = "hsup." + str(self.code) + ".qty"
			if 'name' in data :
				self.regle_id.name = self.name
			if 'majoration' : 
				self.regle_id.amount_percentage = 100 + self.majoration
		else:
			if 'regle_id' not in data or not data['regle_id']:
				cat_id = self.env.ref('oxy_paie.HSUP_DECL')
				type = 'gain'
				condition = "result = contract.schedule_pay == 'monthly' and hsup." + str(self.code) + " or False"
				regle_data={
					'name' : self.name,
					'code' : self.code,
					'sequence' : 402,
					'category_id' : cat_id.id,
					'condition_select' : 'python',
					'condition_python' : condition,
					'amount_select' : 'percentage',
					'amount_percentage_base' : "hsup." + str(self.code) + ".qty",
					'quantity' : 'contract.taux_horaire',
					'amount_percentage' : 100 + res.majoration,
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
		return super(hr_heures_supp_type,self).unlink()