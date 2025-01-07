# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_rappel_type(models.Model):
	_name = 'hr.rappel.type'

	name = fields.Char(string="Désignation")
	code = fields.Char(string="Code")
	cotisable = fields.Boolean(string="Cotisable")
	imposable = fields.Boolean(string="Imposable")
	irg = fields.Boolean(string="IRG 10%")
	type = fields.Selection([('gain', 'Gain'), ('retenu', 'Retenu')],'Type', default='gain')
	regle_id = fields.Many2one('hr.salary.rule', string="Règles salariales")
	name_type = fields.Char('Nom complet', compute="get_complete_name", store=True)
	_rec_name = "name_type"

	_sql_constraints = [
		('code_type_prime', 'unique(code)', 'le code doit être unique !'),
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
			self.irg = True

	@api.depends('name','type')
	def get_complete_name(self):
		for prime in self:
			prime.name_type = '['+ prime.code +'] ' + prime.name +' ('+ prime.type +')'

	@api.model
	def create(self, data):
		res = super(hr_rappel_type,self).create(data)
		type_var = ''
		if not res.regle_id:
			if res.type == 'gain':
				if res.cotisable and res.imposable:
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_PLUS')
					sequence = 280
				elif res.cotisable and res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_IRG_10_PLUS')
					sequence = 280
				elif not res.cotisable and res.imposable:
					categorie = self.env.ref('oxy_paie.RAPPEL_IMPOSABLE_PLUS')
					sequence = 560
				elif not res.cotisable and res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_IRG_10_PLUS')
					sequence = 604
				elif not res.cotisable and not res.imposable and not res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_PLUS')
					sequence = 672
				type_var = 'gain'

			elif res.type == 'retenu':
				if res.cotisable and res.imposable:
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_MOINS')
					sequence = 280
				elif res.cotisable and res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_IRG_10_MOINS')
					sequence = 280
				elif not res.cotisable and res.imposable:
					categorie = self.env.ref('oxy_paie.RAPPEL_IMPOSABLE_MOINS')
					sequence = 560
				elif not res.cotisable and res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_IRG_10_MOINS')
					sequence = 604
				elif not res.cotisable and not res.imposable and not res.irg:
					categorie = self.env.ref('oxy_paie.RAPPEL_MOINS')
					sequence = 672
				type_var = 'retenu'
			
			regle_data = {
				'name' : res.name,
				'code' : res.code,
				'sequence' : sequence,
				'category_id' : categorie.id,
				'condition_select' : 'python',
				'condition_python' : "result = inputs." + str(res.code) + " and inputs." + str(res.code) + " or False",
				'amount_select' : 'code',
				'amount_python_compute' : 'result = inputs.' + str(res.code) +  '.amount',
				'appears_on_payslip' : True,
				'type' : type_var,
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
		return super(hr_rappel_type,self).unlink()


	def write(self,vals):
		res = super(hr_rappel_type,self).write(vals)
		if self.regle_id:
			sequence = self.regle_id.sequence
			categorie = self.regle_id.category_id
			if self.type == 'gain':
				if self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_PLUS')
					sequence = 280
				elif self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_IRG_10_PLUS')
					sequence = 280
				elif not self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_IMPOSABLE_PLUS')
					sequence = 560
				elif not self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_IRG_10_PLUS')
					sequence = 604
				elif not self.cotisable and not self.imposable and not self.irg and ('cotisable' in vals or 'imposable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_PLUS')
					sequence = 672


			elif self.type == 'retenu':
				if self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_MOINS')
					sequence = 280
				elif self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_COTISABLE_IRG_10_MOINS')
					sequence = 280
				elif not self.cotisable and self.imposable and ('cotisable' in vals or 'imposable' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_IMPOSABLE_MOINS')
					sequence = 560
				elif not self.cotisable and self.irg and ('cotisable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_IRG_10_MOINS')
					sequence = 604
				elif not self.cotisable and not self.imposable and not self.irg and ('cotisable' in vals or 'imposable' in vals or 'irg' in vals):
					categorie = self.env.ref('oxy_paie.RAPPEL_MOINS')
					sequence = 672		

		
			
			self.regle_id.name = self.name
			self.regle_id.code = self.code
			self.regle_id.type = self.type
			self.regle_id.sequence = sequence
			self.regle_id.category_id = categorie.id
			self.regle_id.condition_python = "result = inputs." + str(self.code) + " and inputs." + str(self.code) + " or False"
			self.regle_id.amount_python_compute = 'result = inputs.' + str(self.code) +  '.amount'

		return res