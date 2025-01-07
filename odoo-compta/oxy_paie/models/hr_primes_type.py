# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_primes_type(models.Model):
	_name = 'hr.primes.type'
	_rec_name = "name_type"
	_order = "code"

	name = fields.Char(string="Désignation")
	code = fields.Char(string="Code")
	cotisable = fields.Boolean(string="Cotisable")
	imposable = fields.Boolean(string="Imposable")
	irg = fields.Boolean(string="IRG 10%")
	type = fields.Selection([('fix', 'Fix'), ('taux', 'Taux'), ('prorata', 'Prorata')],'Type', default='fix')
	regle_id = fields.Many2one('hr.salary.rule', string="Règles salariales")
	name_type = fields.Char('Nom complet', compute="get_complete_name", store=True)

	_sql_constraints = [
		('code_type_prime', 'unique(code,type)', 'le code doit être unique !'),
	]

	@api.onchange('cotisable')
	def on_change_cotisable(self):
		if self.cotisable:
			self.imposable = True

	@api.onchange('imposable')
	def on_change_imposable(self):
		if self.imposable:
			self.irg = False
		elif self.cotisable:
			self.irg = True

	@api.onchange('irg')
	def on_change_irg(self):
		if self.irg:
			self.imposable = False
		elif self.cotisable:
			self.imposable = True

	@api.depends('name','type')
	def get_complete_name(self):
		for prime in self:
			prime.name_type = '['+ prime.code +'] ' + prime.name +' ('+ prime.type +')'


	@api.model
	def create(self, data):
		res = super(hr_primes_type,self).create(data)
		if not res.regle_id:
			if res.cotisable and res.imposable:
				regle = self.env['hr.salary.rule'].search([('code','=',res.code)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 473
				categorie = self.env.ref('oxy_paie.PRIME_COTISABLE_IMPOSABLE')

			elif res.cotisable and res.irg:
				regle = self.env['hr.salary.rule'].search([('code','=',res.code)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 480
				categorie = self.env.ref('oxy_paie.PRIME_COTISABLE_IRG_10')

			elif not res.cotisable and res.imposable:
				regle = self.env['hr.salary.rule'].search([('code','=',res.code)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 510
				categorie = self.env.ref('oxy_paie.PRIME_IMPOSABLE')

			elif not res.cotisable and res.irg:
				regle = self.env['hr.salary.rule'].search([('code','=',res.code)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 511
				categorie = self.env.ref('oxy_paie.PRIME_IRG_10')

			else:
				sequence = 613
				categorie = self.env.ref('oxy_paie.PRIME')

			if res.type == 'taux':
				regle_data={
					'name' : res.name,
					'code' : res.code,
					'sequence' : sequence,
					'category_id' : categorie.id,
					'condition_select' : 'python',
					'condition_python' : "result = inputs." + str(res.code) + " and inputs." + str(res.code) + ".type_p == 'taux' or False",
					'amount_select' : 'code',
					'amount_python_compute' : 'result = prime_taux(inputs.' + str(res.code) +  '.amount,(categories.SAL_BASE_MENSUELLE - categories.MONTANT_ABSENCE))',
					'appears_on_payslip' : True,
					'type' : 'gain',
				}

			elif res.type == 'prorata':
				regle_data={
					'name' : res.name,
					'code' : res.code,
					'sequence' : sequence,
					'category_id' : categorie.id,
					'condition_select' : 'python',
					'condition_python' : "result = inputs." + str(res.code) + " and inputs." + str(res.code) + ".type_p == 'prorata' or False",
					'amount_select' : 'code',
					'amount_python_compute' : 'result = prime_prorata(inputs.' + str(res.code) +  '.amount,payslip.abs_justifies)',
					'appears_on_payslip' : True,
					'type' : 'gain',
				}

			elif res.type == 'fix':
				regle_data={
					'name' : res.name,
					'code' : res.code,
					'sequence' : sequence,
					'category_id' : categorie.id,
					'condition_select' : 'python',
					'condition_python' : "result = inputs." + str(res.code) + " and inputs." + str(res.code) + ".type_p == 'fix' or False",
					'amount_select' : 'code',
					'amount_python_compute' : 'result = inputs.' + str(res.code) +  '.amount',
					'appears_on_payslip' : True,
					'type' : 'gain',
				}

			regle_id_tmp = self.env['hr.salary.rule'].create(regle_data)
			res.regle_id = regle_id_tmp.id
			struct_id = self.env.ref('oxy_paie.hr_payroll_salary_structure_heure')
			struct_id.rule_ids = [(4,regle_id_tmp.id)]
		return res

	
	def unlink(self):
		for rec in self:
			if rec.regle_id:
				rec.regle_id.unlink()
		return super(hr_primes_type,self).unlink()


	def write(self,vals):
		res = super(hr_primes_type,self).write(vals)
		if self.regle_id:
			sequence = self.regle_id.sequence
			categorie = self.regle_id.category_id
			if self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
				categorie = self.env.ref('oxy_paie.PRIME_COTISABLE_IMPOSABLE')
				regle = self.env['hr.salary.rule'].search([('code','=',self.code),('category_id','=',categorie.id)],limit=1) 
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 473
			elif self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
				categorie = self.env.ref('oxy_paie.PRIME_COTISABLE_IRG_10')
				regle = self.env['hr.salary.rule'].search([('code','=',self.code),('category_id','=',categorie.id)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 480

			elif not self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
				categorie = self.env.ref('oxy_paie.PRIME_IMPOSABLE')
				regle = self.env['hr.salary.rule'].search([('code','=',self.code),('category_id','=',categorie.id)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 510

			elif not self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
				categorie = self.env.ref('oxy_paie.PRIME_IRG_10')
				regle = self.env['hr.salary.rule'].search([('code','=',self.code),('category_id','=',categorie.id)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					sequence = 511

			elif not self.cotisable and not self.imposable and ('cotisable' in vals or 'imposable' in vals):
				categorie = self.env.ref('oxy_paie.PRIME')
				regle = self.env['hr.salary.rule'].search([('code','=',self.code),('category_id','=',categorie.id)],limit=1)
				if regle and regle.type == 'gain':
					sequence = regle.sequence
				else:
					regle_browse = self.env['hr.salary.rule'].search([('sequence','>=','607'),('sequence','<','650')])
					regle_list = []
					for reg in regle_browse:
						regle_list.append(reg.sequence)
					if (max(regle_list) + 1) > 649:
						sequence = 649
					else:
						sequence = max(regle_list) + 1

			if self.type == 'taux':
				self.regle_id.name = self.name
				self.regle_id.code = self.code
				self.regle_id.sequence = sequence
				self.regle_id.category_id = categorie.id
				self.regle_id.condition_python = "result = inputs." + str(self.code) + " and inputs." + str(self.code) + ".type_p == 'taux' or False"
				self.regle_id.amount_python_compute = 'result = prime_taux(inputs.' + str(self.code) +  '.amount,(categories.SAL_BASE_MENSUELLE - categories.MONTANT_ABSENCE))'

			elif self.type == 'prorata':
				self.regle_id.name = self.name
				self.regle_id.code = self.code
				self.regle_id.sequence = sequence
				self.regle_id.category_id = categorie.id
				self.regle_id.condition_python = "result = inputs." + str(self.code) + " and inputs." + str(self.code) + ".type_p == 'prorata' or False"
				self.regle_id.amount_python_compute = 'result = prime_prorata(inputs.' + str(self.code) +  '.amount,payslip.abs_justifies)'

			elif self.type == 'fix':
				self.regle_id.name = self.name
				self.regle_id.code = self.code
				self.regle_id.sequence = sequence
				self.regle_id.category_id = categorie.id
				self.regle_id.condition_python = "result = inputs." + str(self.code) + " and inputs." + str(self.code) + ".type_p == 'fix' or False"
				self.regle_id.amount_python_compute = 'result = inputs.' + str(self.code) +  '.amount'

		return res