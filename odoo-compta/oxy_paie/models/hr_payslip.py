# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from datetime import date, datetime, time as time_date
from dateutil.relativedelta import relativedelta
import calendar
import babel
from . import outils
from odoo import tools
import calendar
from pytz import utc
from odoo.addons.resource.models.resource import datetime_to_string
from odoo.exceptions import ValidationError


class hr_payslip(models.Model):
	_inherit = 'hr.payslip'

	nbr_jr_panier = fields.Integer(string='Nombre de jour de panier', default=22)
	nbr_jr_transport = fields.Integer(string='Nombre de jour de transport', default=22)
	type_bulletin = fields.Selection([('normal', 'Normal'),('stc', 'Stc')],'Type', default='normal')
	indem_licen = fields.Float(string="Indemnité de licenciement")
	motif = fields.Text(string="Motif")
	hsup_line_ids = fields.One2many('hr.payslip.heure.sup','payslip_id')
	input_line_ids = fields.One2many(copy=True)
	#isNew = fields.Boolean(compute="get_isnew",store=True)
	calcul_reel = fields.Boolean('Calcul réel?', compute="get_type_calcul", store=True)
	abs_justifies = fields.Float('Absences justifiés', compute="get_abs_justifie", store=True)
	iep_eff = fields.Float('IEP')
	nb_leaves = fields.Float('# jour de congé (weekend inclus)', compute="get_nb_leaves", store=True)
	avoir_payslip = fields.Many2one('hr.payslip', string='Payslip avoir')
	conge_restant = fields.Float(string='Congé restant')
	holiday_att_id = fields.Many2one('hr.leave.allocation')
	have_credit_note = fields.Boolean('Have credit note')

	_sql_constraints = [
		('pays_unique', 'UNIQUE(employee_id, date_from, date_to, credit_note, have_credit_note)', 'Fiche de paie existe déjà pour cette période!'),
	]

	def refund_sheet(self):
		for payslip in self:
			copied_payslip = payslip.copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
			payslip.avoir_payslip = copied_payslip.id
			payslip.have_credit_note = True
			copied_payslip.action_payslip_done()
		formview_ref = self.env.ref('om_hr_payroll.view_hr_payslip_form', False)
		treeview_ref = self.env.ref('om_hr_payroll.view_hr_payslip_tree', False)
		return {
			'name': ("Refund Payslip"),
			'view_mode': 'tree, form',
			'view_id': False,
			'view_type': 'form',
			'res_model': 'hr.payslip',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
			'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
			'context': {}
		}

	@api.depends('date_from', 'date_to', 'employee_id')
	def get_nb_leaves(self):
		for res in self:
			nb_leaves = 0
			if res.employee_id:
				day_from = datetime.combine(res.date_from, time_date.min)
				day_to = datetime.combine(res.date_to, time_date.max)
				if not day_from.tzinfo:
					day_from = day_from.replace(tzinfo=utc)
				if not day_to.tzinfo:
					day_to = day_to.replace(tzinfo=utc)

				domain = [
					('calendar_id', '=', res.employee_id.resource_calendar_id.id),
					('resource_id', '=', res.employee_id.resource_id.id),
					('date_from', '<=', datetime_to_string(day_to)),
					('date_to', '>=', datetime_to_string(day_from))]
				for leave in self.env['resource.calendar.leaves'].search(domain):
					if leave.holiday_id.holiday_status_id.absence_type.code == 'R093':
						nb_leaves += leave.holiday_id.number_of_days_display
			res.nb_leaves = nb_leaves

	def get_periode(self):
		ttyme = self.date_to
		locale = self.env.context.get('lang') or 'en_US'
		return (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM y', locale=locale))).title()

	def get_net(self):
		for rule in self.details_by_salary_rule_category:
			if rule.code == "SALNETP":
				return rule.total

	def get_totals(self):
		somme_gain = 0
		somme_retenu = 0
		for line in self.line_ids:
			if line.salary_rule_id.type == 'gain':
				somme_gain += line.total

			if line.salary_rule_id.type == 'retenu':
				somme_retenu += line.total
		return [somme_gain, somme_retenu]

	def get_base(self,line):
		tmp = 0
		if line.amount_select == 'percentage':
			tmp = line.amount
		elif line.code == 'R660':
			for rule in self.line_ids:
				if rule.code in ('SIMP', 'BIMP'):
					tmp = rule.total
		elif line.code == 'R002':
			if self.contract_id.schedule_pay == 'monthly':
				if self.calcul_reel:
					for rule in self.line_ids:
						if rule.code in ('NHT'):
							tmp = rule.total
				else:
					tmp = 173.33
			elif self.contract_id.schedule_pay == 'horaire':
				for rule in self.line_ids:
					if rule.code in ('NHT'):
						tmp = rule.total
			else:
				for rule in self.line_ids:
					if rule.code in ('NJT'):
						tmp = rule.total
		elif line.code == 'SBAMJ':
			tmp = 173.33
		elif line.code == 'R260':
			sbam = 0
			mabs = 0
			for rule in self.line_ids:
				if rule.code in ('R002'):
					sbam = rule.total
				if rule.category_id.code == 'MONTANT_ABSENCE':
					mabs += rule.total
			tmp = sbam - mabs 
		else:
			tmp = 0
		return tmp

	def get_taux(self, line):
		if line.amount_select == 'percentage':
			return line.quantity
		elif line.amount_select == 'fix':
			return line.amount
		elif line.code in ('R002', 'SBAMJ'):
			if self.contract_id.schedule_pay in ('monthly'):
				return self.contract_id.taux_horaire
			else:
				for c in self.line_ids:
					if c.code == 'TJOR':
						return c.total
		elif line.code == 'R260':
			return line.slip_id.iep_eff
		return ''

	@api.depends('worked_days_line_ids','worked_days_line_ids.number_of_hours')
	def get_abs_justifie(self):
		for res in self:
			abs_justifie = 0
			for line in res.worked_days_line_ids:
				if line.code not in  ("WORK100",'R093'):
					abs_justifie += line.number_of_hours
			res.abs_justifies = abs_justifie

	def get_date_start(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start = ICPSudo.get_param('oxy_paie.day_start') and ICPSudo.get_param('oxy_paie.day_start') or 1
		return fields.Date.to_string(date.today().replace(day=int(day_start)))

	def get_date_end(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_end = ICPSudo.get_param('oxy_paie.day_end')
		date_end = day_end and fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=int(day_end))).date()) or fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
		return date_end

	date_from = fields.Date(default=get_date_start)
	date_to = fields.Date(default=get_date_end)

	@api.depends('date_from','date_to', 'employee_id')
	def get_type_calcul(self):
		for res in self:
			if res.contract_id:
				d_to_date = fields.Date.from_string(res.date_to)
				from_date = fields.Date.from_string(res.date_from)
				date_fin_prev = from_date + relativedelta(months=+1, days=-1)
				start_date = fields.Date.from_string(res.contract_id.date_start)
				if d_to_date < date_fin_prev or start_date > from_date:
					res.calcul_reel = True
				else:
					res.calcul_reel = False
			else:
				res.calcul_reel = False

	@api.model
	def get_worked_day_lines(self, contracts, date_from, date_to, calcul_reel=False):
		#les absences
		if self:
			if date_from < self.contract_id.date_start:# pour les nouveaux
				date_from = self.contract_id.date_start
		else:
			if date_from < contracts[0].date_start:# pour les nouveaux
				date_from = contracts[0].date_start

		res = super(hr_payslip,self).get_worked_day_lines(contracts,date_from,date_to)
		if not calcul_reel and res:
			res[0]['number_of_hours'] = 173.33
			res[0]['number_of_days'] = 21.66
		working_hours_on_day = contracts.resource_calendar_id.hours_per_day
		empl_id = contracts.employee_id
		contract_id = contracts.id
		absences = {}
		absence_ids = self.env['hr.absences'].search([('employee_id','=',empl_id.id),('date','>=',date_from),('date','<=',date_to)])
		for abs in absence_ids:
			if abs.absence_type.id not in absences:
				absences[abs.absence_type.id] = abs.qte
			else:
				absences[abs.absence_type.id] += abs.qte
		nb_hours_conge = 0
		nb_jour_conge = 0
		worked_days_to_delete = []

		#ajout congé dans liste abs
		for r in res:
			if r['code'] != 'WORK100':
				leave_type = self.env['hr.leave.type'].search([('name','=',r['name'])],limit=1)
				if leave_type and leave_type.absence_type:
					absences[leave_type.absence_type.id] = r['number_of_hours']
					nb_hours_conge += r['number_of_hours']
					nb_jour_conge += r['number_of_days']
					worked_days_to_delete.append(r)
			else:
				r['number_of_hours'] += nb_hours_conge
				r['number_of_days'] += nb_jour_conge

		abs_somme = 0
		for absce in absences:
			abs_id = self.env['hr.absence.type'].browse(absce)
			abs_somme += absences[absce]
			res.append({
				'name': abs_id.name,
				'code': abs_id.code,
				'number_of_days': absences[absce] / working_hours_on_day,
				'number_of_hours': absences[absce],
				'contract_id': contract_id,
				'sequence' : 5,
			})
		if res and not calcul_reel:
			res[0]['number_of_hours'] -= abs_somme 
			res[0]['number_of_days'] -= abs_somme / working_hours_on_day 
		for leave in worked_days_to_delete:
			res.remove(leave)
		return res

	@api.model
	def get_worked_sup_lines(self, contracts, date_from, date_to):
		#get heures sup
		res = []
		for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
			sup_lines = self.env['hr.heures.supp'].search([('employee_id','=',contract.employee_id.id), ('date','>=',date_from), ('date','<=',date_to)])
			sups = {}
			for line in sup_lines:
				if line.type_id.id not in sups:
					sups[line.type_id.id] = line.qte
				else:
					sups[line.type_id.id] += line.qte
			for sup_id in sups:
				sup = self.env['hr.heures.supp.type'].browse(sup_id)
				hsup = {
					'name' : sup.name,
					'code' : sup.code,
					'qty' : sups[sup_id],
					'pourcentage' : sup.majoration,
					'contract_id' : contract.id
				}
				res.append(hsup)
		return res

	@api.onchange('employee_id', 'date_from', 'date_to', 'type_bulletin')
	def onchange_employee(self):
		res = super(hr_payslip,self).onchange_employee()
		if self.date_to and self.date_from:
			date_fin_prev = self.date_from + relativedelta(months=+1, days=-1)
			if self.contract_id:
				if self.date_to < date_fin_prev or self.contract_id.date_start > self.date_from:
					calcul_reel = True
				else:
					calcul_reel = False

			else:
				calcul_reel = False

		contract_ids = self.get_contract(self.employee_id, self.date_from, self.date_to)
		contracts = self.env['hr.contract'].browse(contract_ids)
		if self.contract_id:
			worked_days_line_ids = self.get_worked_day_lines(contracts, self.date_from, self.date_to, calcul_reel)
			worked_days_lines = self.worked_days_line_ids.browse([])
			for r in worked_days_line_ids:
				worked_days_lines += worked_days_lines.new(r)
			self.worked_days_line_ids = worked_days_lines
			locale = self.env.context.get('lang') or 'en_US'
			self.iep_eff = self.compute_iep(self.contract_id.date_start, self.employee_id.date_entree, self.date_to, self.employee_id.hors_societe)
			if self.type_bulletin == 'normal':
				self.name =  _('Salary Slip of %s for %s') % (self.employee_id.name, babel.dates.format_date(date=self.date_to, format='MMMM-y', locale=locale))
			else:
				self.name = _('STC de %s pour %s') % (self.employee_id.name, self.date_to.strftime('%B-%Y'))

			hsup_line_ids = self.get_worked_sup_lines(contracts, self.date_from, self.date_to)
			hsup_lines = self.hsup_line_ids.browse([])
			for r in hsup_line_ids:
				hsup_lines += hsup_lines.new(r)
			self.hsup_line_ids = hsup_lines


			input_line_ids = self.get_inputs(contracts, self.date_from, self.date_to, self.type_bulletin)
			input_lines = self.input_line_ids.browse([])
			for r in input_line_ids:
				input_lines += input_lines.new(r)
			self.input_line_ids = input_lines
			if self.type_bulletin == 'stc' :
				conge_ids = self.env['hr.conge'].search([('employee_id','=',self.employee_id.id), ('nb_jour_restant','>',0)])
				montant = 0
				for conge in conge_ids:
					montant += conge.ica_restant
				self.conge_restant = montant
		return

	def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
		res = super(hr_payslip,self).onchange_employee_id(date_from, date_to, employee_id, contract_id)
		employee = self.env['hr.employee'].browse(employee_id)
		if not self.env.context.get('contract'):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(employee, date_from, date_to)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(employee, date_from, date_to)
		contract = self.env['hr.contract'].browse(contract_ids[0])
		if contract:
			#d_to_date = fields.Date.from_string(date_to)
			#from_date = fields.Date.from_string(date_from)
			date_fin_prev = date_from + relativedelta(months=+1, days=-1)
			if self.contract_id:
				if date_to < date_fin_prev or self.contract_id.date_start > self.date_from:
					calcul_reel = True
				else:
					calcul_reel = False
			else:
				calcul_reel = False
		else:
			calcul_reel = False
		contracts = self.env['hr.contract'].browse(contract_ids)
		worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to, calcul_reel)
		worked_sup_lines = self.get_worked_sup_lines(contracts, date_from, date_to)
		employee = self.env['hr.employee'].browse(employee_id)
		iep_eff = self.compute_iep(contract.date_start, employee.date_entree, fields.Date.from_string(date_to), employee.hors_societe)
		res['value'].update({
			'name' : _('Salary Slip of %s for %s') % (employee.name, date_to.strftime('%B-%Y')),
			'worked_days_line_ids': worked_days_line_ids,
			'hsup_line_ids' : worked_sup_lines,
			'calcul_reel' : calcul_reel,
			'iep_eff' : iep_eff,
		})
		return res

	def compute_iep(self, date_recrutement, date_entre, date_fin, iep_man):
		res = 0
		DATETIME_FORMAT = "%Y-%m-%d"
		if date_entre:
			date_rec = datetime.strptime(datetime.strftime(date_entre, DATETIME_FORMAT), DATETIME_FORMAT)
		else:
			date_rec = datetime.strptime(datetime.strftime(date_recrutement, DATETIME_FORMAT), DATETIME_FORMAT)
		date_fin = datetime.strptime(datetime.strftime(date_fin, DATETIME_FORMAT), DATETIME_FORMAT)
		
		timedelta = date_fin - date_rec
		diff_day = int((timedelta.days + float(timedelta.seconds) / 86400) / 365)
		if int(date_rec.strftime('%m')) == int(date_fin.strftime('%m')) and int(date_rec.strftime('%d')) > 14:
			if diff_day>0:
				diff_day -= 1
		res = diff_day + iep_man
		return res

	@api.model
	def get_inputs(self, contracts, date_from, date_to, type_bulletin = 'normal'):
		#Prêt
		res = super(hr_payslip,self).get_inputs(contracts,date_from,date_to)
		contract_id = contracts.id
		employee_id = contracts.employee_id.id
		if type_bulletin == 'normal':
			pret = self.env['hr.prets.lines'].search([('prets_id.employee_id','=',employee_id),('prets_id.state','=','done'),('state','=','attente'),('date','>=',date_from),('date','<=',date_to)])
		else:
			pret = self.env['hr.prets.lines'].search([('prets_id.employee_id','=',employee_id),('prets_id.state','=','done'),('state','=','attente')])
		pret_montant = 0
		pret_id = []
		for p in pret:
			pret_montant += p.montant
			pret_id.append(p.id)
		if pret_montant > 0:
			res.append({
				'name' : 'Prêt',
				'code' : 'R724',
				'amount' : pret_montant,
				'list_id_prets' : [(6,0,pret_id)],
				'contract_id' : contract_id,
			})
		#Avance
		avances = self.env['hr.avance'].search([('employee_id','=',employee_id),('date','>=',date_from),('date','<=',date_to)])
		if avances:
			avance_amount = sum(av.amount for av in avances)
			res.append({
				'name' : 'Avance sur salaire',
				'code' : 'AVS',
				'amount' : avance_amount,
				'contract_id' : contract_id,
			})
		#Primes
		primes = self.env['hr.primes.lines'].search([('employee_id','=',employee_id),('state','=','valide')])
		month = date_to.strftime('%m')
		for prime in primes:
			if (prime.hr_primes_id.affectation in ('ocasionnel', 'mensuel')) or (prime.hr_primes_id.affectation == 'annuel' and month == prime.hr_primes_id.month):
				res.append({
					'name' : prime.hr_primes_id.primes_type_id.name,
					'code' : prime.hr_primes_id.primes_type_id.code,
					'amount' : prime.taux_montant,
					'type_p' : prime.hr_primes_id.primes_type_id.type,
					'prime_id' : prime.hr_primes_id.id,
					'contract_id' : contract_id,
				})
			elif prime.hr_primes_id.affectation == 'periodique':
				date_from = datetime.strptime('01-'+str(prime.hr_primes_id.date_from),'%d-%m-%Y').date()
				date_to = datetime.strptime(str(date_to.day)+'-'+str(prime.hr_primes_id.date_to),'%d-%m-%Y').date()
				if self.date_to >= date_from and self.date_to <= date_to:
					res.append({
						'name' : prime.hr_primes_id.primes_type_id.name,
						'code' : prime.hr_primes_id.primes_type_id.code,
						'amount' : prime.taux_montant,
						'type_p' : prime.hr_primes_id.primes_type_id.type,
						'prime_id' : prime.id,
						'contract_id' : contract_id,
					})
		#rappel
		rappels = self.env['hr.rappel'].search([('employee_id','=',employee_id),('date','>=',date_from),('date','<=',date_to)])
		rappel_type = []
		for rappel in rappels:
			if rappel.rappel_type_id.id not in rappel_type:
				rappel_type.append(rappel.rappel_type_id.id)
		for rappel_type in rappel_type:
			somme = 0
			for rappel in rappels:
				if rappel.rappel_type_id.id == rappel_type:
					somme += rappel.taux_montant
			rappel_obj = self.env['hr.rappel.type'].browse(rappel_type)
			res.append({
				'name' : rappel_obj.name,
				'code' : rappel_obj.code,
				'amount' : somme,
				'contract_id' : contract_id,
			})
		return res

	def action_payslip_done(self):
		res = super(hr_payslip, self).action_payslip_done()
		for payslip in self:
			for input in payslip.input_line_ids:
				#Prets

				for pret in input.list_id_prets:
					if not payslip.credit_note:
						pret.state = 'rembourser'
					else:
						#avoir
						pret.state = 'attente'

				#Prime
				if input.prime_id:
					if not payslip.credit_note:
						input.prime_id.state = 'archiver'
						if not any([line.state == 'valide' for line in input.prime_id.hr_primes_id.hr_primes_line_ids]) and input.prime_id.hr_primes_id.affectation == 'periodique':
							input.prime_id.hr_primes_id.state = 'archiver'
					else:
						#avoir
						input.prime_id.state = 'valide'
						input.prime_id.hr_primes_id.state = 'valide'
			#ICA
			if payslip.type_bulletin == 'normal':
				if payslip.nb_leaves > 0:
					conge_ids = self.env['hr.conge'].search([('employee_id','=',payslip.employee_id.id),('nb_jour_restant','>',0)])
					if not payslip.credit_note:
						qte = int(payslip.nb_leaves)
					else:
						#avoir
						qte = int(payslip.nb_leaves) * -1

					ica = 0
					for conge in conge_ids:
						if qte > conge.nb_jour_restant:
							ica += conge.ica_restant
							qte -= conge.nb_jour_restant
							conge.ica_restant = 0
							conge.nb_jour_restant = 0
						else:
							tmp_poste = qte * conge.ica_restant / conge.nb_jour_restant
							ica += tmp_poste
							conge.nb_jour_restant -= qte
							conge.ica_restant -= tmp_poste
							break
				nb_jour = 0
				ica = 0
				for line in payslip.line_ids:
					if line.total > 15:
						nb_jour = 2.5
						if not payslip.credit_note:
							if line.code == 'R020':
								holiday = self.env['hr.leave.allocation'].create({
									'name' : 'Congé ' + payslip.date_to.strftime('%Y'),
									'holiday_status_id' : self.env.ref('oxy_paie.holiday_status_detente').id,
									'number_of_days' : nb_jour,
									'holiday_type' : 'employee',
									'employee_id' : payslip.employee_id.id,
								})
								payslip.holiday_att_id = holiday.id
								holiday.action_approve()
								#pour double validation
								if holiday.state in ('confirm','validate1'):
									holiday.action_validate()
					if line.code == 'SPOST':
						ica = line.total / 12
				if payslip.credit_note and payslip.holiday_att_id:
					#avoir
					payslip.holiday_att_id.action_refuse()
					payslip.holiday_att_id.action_draft()
					payslip.holiday_att_id.unlink()
				#cumul congé
				ICPSudo = self.env['ir.config_parameter'].sudo()
				day_start = ICPSudo.get_param('oxy_paie.day_start') and ICPSudo.get_param('oxy_paie.day_start') or 1
				day_end = ICPSudo.get_param('oxy_paie.day_end')
				date_start = date.today().replace(day=int(day_start), month=int(self.struct_id.conge_du))
				if int(self.struct_id.conge_au) < int(self.struct_id.conge_du):
					date_end = day_end and (datetime.now() + relativedelta(years=+1, month=int(self.struct_id.conge_au), day=int(day_end))).date() or \
							(datetime.now() + relativedelta(years=+1, month=int(self.struct_id.conge_au), day=1, days=-1)).date()
				else:
					date_end = day_end and (datetime.now() + relativedelta(month=int(self.struct_id.conge_au), day=int(day_end))).date() or \
							(datetime.now() + relativedelta(month=int(self.struct_id.conge_au), day=1, days=-1)).date()
				if (self.date_to.year == date_start.year and self.date_to.month < date_start.month) or self.date_to.year < date_start.year:
					year = self.date_to.year
				else:
					year = self.date_to.year + 1
				conge = self.env['hr.conge'].search([('employee_id','=',self.employee_id.id),('year','=',year)])
				if not payslip.credit_note:
					if conge:
						conge.ica += ica
						conge.ica_restant += ica
						conge.nb_jour += nb_jour
						conge.nb_jour_restant += nb_jour
					else:
						self.env['hr.conge'].create({
							'employee_id' : payslip.employee_id.id,
							'year' : year,
							'ica' : ica,
							'ica_restant' : ica,
							'nb_jour' : nb_jour,
							'nb_jour_restant' : nb_jour,
						})
				else:
					#avoir
					conge.ica -= ica
					conge.ica_restant -= ica
					conge.nb_jour -= nb_jour
					conge.nb_jour_restant -= nb_jour
			else:
				if not payslip.motif:
					raise ValidationError(('Veuillez renseigner le motif de départ SVP!'))
				conges = self.env['hr.conge'].search([('employee_id','=',payslip.employee_id.id)])
				if not payslip.credit_note:
					for conge in conges:
						conge.ica_stc = conge.ica_restant
						conge.nb_jour_stc = conge.nb_jour_restant
					conges.write({
							'ica_restant' : 0,
							'nb_jour_restant' : 0,
						})
					payslip.employee_id.non_actif = True
					payslip.employee_id.date_sortie = payslip.date_to
					payslip.employee_id.motif = payslip.motif
				else:
					# avoir
					for conge in conges:
						conge.ica_restant = conge.ica_stc
						conge.nb_jour_restant = conge.nb_jour_stc
					payslip.employee_id.non_actif = False
		return res

	@api.model
	def _get_payslip_lines(self, contract_ids, payslip_id):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
			return localdict

		class BrowsableObject(object):
			def __init__(self, employee_id, dict, env):
				self.employee_id = employee_id
				self.dict = dict
				self.env = env

			def __getattr__(self, attr):
				return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(amount) as sum
					FROM hr_payslip as hp, hr_payslip_input as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()[0] or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
					FROM hr_payslip as hp, hr_payslip_worked_days as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()

			def sum(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[0] or 0.0

			def sum_hours(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[1] or 0.0

		class Payslips(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
							FROM hr_payslip as hp, hr_payslip_line as pl
							WHERE hp.employee_id = %s AND hp.state = 'done'
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
							(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()
				return res and res[0] or 0.0

		class HsupLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			
			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = datetime.now().strftime('%Y-%m-%d')
				result = 0.0
				self.cr.execute("SELECT sum(amount) as sum\
							FROM hr_payslip as hp, hr_payslip_hsup as pi \
							WHERE hp.employee_id = %s AND hp.state = 'done' \
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
						   (self.employee_id, from_date, to_date, code))
				res = self.cr.fetchone()[0]
				return res or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules_dict = {}
		worked_days_dict = {}
		inputs_dict = {}
		blacklist = []
		hsup = {}
		payslip = self.env['hr.payslip'].browse(payslip_id)
		for worked_days_line in payslip.worked_days_line_ids:
			worked_days_dict[worked_days_line.code] = worked_days_line
		for input_line in payslip.input_line_ids:
			inputs_dict[input_line.code] = input_line
		for hsup_line in payslip.hsup_line_ids:
			hsup[hsup_line.code] = hsup_line


		categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
		inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
		worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
		payslips = Payslips(payslip.employee_id.id, payslip, self.env)
		rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
		hsup_obj = HsupLine(payslip.employee_id.id, hsup, self.env)

		baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs, 'hsup' : hsup_obj}
		#get the ids of the structures on the contracts and their parent id as well
		contracts = self.env['hr.contract'].browse(contract_ids)
		if len(contracts) == 1 and payslip.struct_id:
			structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
		else:
			structure_ids = contracts.get_all_structures()
		#get the rules of the structure and thier children
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
		sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

		################## IRG ###################
		
		def calc_irg(sal_impo):
			sal_impo_str = str(int(sal_impo))
			sal_impo_list = list(sal_impo_str)
			sal_impo_list[-1] = "0"
			sal_impo_str = ''.join(sal_impo_str for sal_impo_str in sal_impo_list)
			sal_impo_int = int(sal_impo_str)
			irg = 0
			tranche1 = 10000
			tranche2 = 20000
			tranche3 = 90000
			if sal_impo_int <= 10000:
				tmp_irg = 0
			elif sal_impo_int <= 30000:
				tmp_irg = (sal_impo_int - tranche1)*0.2
			elif sal_impo_int <= 120000:
				tmp_irg = tranche2 * 0.2 + (sal_impo_int - tranche1 - tranche2) * 0.3
			else:
				tmp_irg = tranche2 * 0.2 + tranche3 * 0.3 + (sal_impo_int - 10000 - 20000 - 90000) * 0.35
			abat = tmp_irg * 0.4
			if abat > 1000 and abat <= 1500:
				irg = tmp_irg - abat
			elif abat > 1500:
				irg = tmp_irg - 1500
			elif abat <= 1000:
				irg = tmp_irg - 1000
			if irg < 0:
				irg = 0
			# IRG 2020
			if sal_impo_int <= 30000:
				irg = 0
			elif sal_impo_int > 30000 and sal_impo_int < 35000:
				irg = round(irg * 137/51 - 27925/8)
			return irg
		
		def calc_conge(employee_id, nb_jour, date_to):
			conge_ids = self.env['hr.conge'].search([('employee_id','=',employee_id.id), ('nb_jour_restant','>',0)])
			qte = int(nb_jour)
			ica = 0
			for conge in conge_ids:
				if qte > conge.nb_jour_restant:
					ica += conge.ica_restant
					qte -= conge.nb_jour_restant
				else:
					tmp_poste = qte * conge.ica_restant / conge.nb_jour_restant
					ica += tmp_poste
					break
			return ica

		######## Fin ###########
		for contract in contracts:
			employee = contract.employee_id
			localdict = dict(baselocaldict, employee=employee, contract=contract)
			for rule in sorted_rules:
				key = rule.code + '-' + str(contract.id)
				localdict['result'] = None
				localdict['result_qty'] = 1.0
				localdict['result_rate'] = 100
				#####################
				
				localdict['nb_jour_mois'] = outils.nb_jour_mois
				localdict['calcul_iep'] = outils.calcul_iep
				localdict['prime_prorata'] = outils.prime_prorata
				localdict['prime_taux'] = outils.prime_taux
				localdict['irg10'] = outils.irg10
				localdict['truncate'] = outils.truncate
				localdict['get_prime_asiduite'] = outils.get_prime_asiduite
				localdict['get_prime_rendement'] = outils.get_prime_rendement
				localdict['get_nb_mois_travailler'] = outils.get_nb_mois_travailler
				localdict['calc_irg'] = calc_irg
				localdict['calc_conge'] = calc_conge

				#check if the rule can be applied
				if rule._satisfy_condition(localdict) and rule.id not in blacklist:
					#compute the amount of the rule
					amount, qty, rate = rule._compute_rule(localdict)
					#check if there is already a rule computed with that code
					previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
					#set/overwrite the amount computed for this rule in the localdict
					tot_rule = amount * qty * rate / 100.0
					localdict[rule.code] = tot_rule
					rules_dict[rule.code] = rule
					#sum the amount for its salary category
					localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
					#create/overwrite the rule in the temporary results
					result_dict[key] = {
						'salary_rule_id': rule.id,
						'contract_id': contract.id,
						'name': rule.name,
						'code': rule.code,
						'category_id': rule.category_id.id,
						'sequence': rule.sequence,
						'appears_on_payslip': rule.appears_on_payslip,
						'condition_select': rule.condition_select,
						'condition_python': rule.condition_python,
						'condition_range': rule.condition_range,
						'condition_range_min': rule.condition_range_min,
						'condition_range_max': rule.condition_range_max,
						'amount_select': rule.amount_select,
						'amount_fix': rule.amount_fix,
						'amount_python_compute': rule.amount_python_compute,
						'amount_percentage': rule.amount_percentage,
						'amount_percentage_base': rule.amount_percentage_base,
						'register_id': rule.register_id.id,
						'amount': amount,
						'employee_id': contract.employee_id.id,
						'quantity': qty,
						'rate': rate,
					}
				else:
					#blacklist this rule and its children
					blacklist += [id for id, seq in rule._recursive_search_of_rules()]
		return list(result_dict.values())

class hr_payslip_input(models.Model):
	_inherit = 'hr.payslip.input'

	type_p = fields.Selection([('prorata', 'Prorata'), ('taux', 'Taux'), ('fix', 'Fix')],'Type',)
	list_id_prets = fields.Many2many('hr.prets.lines')
	prime_id = fields.Many2one('hr.primes.lines',string="Prime")

class hr_payslip_heure_sup(models.Model):
	_name = 'hr.payslip.heure.sup'

	name = fields.Char(string='Description')
	code = fields.Char(string='Code')
	qty = fields.Float(string='Quantité')
	pourcentage = fields.Integer(string='Pourcentage')
	contract_id = fields.Many2one('hr.contract', 'Contrat')
	payslip_id = fields.Many2one('hr.payslip', string='Payslip', ondelete='cascade')

class HrPayslipRun(models.Model):
	_inherit = 'hr.payslip.run'

	def get_date_start(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start = ICPSudo.get_param('oxy_paie.day_start') and ICPSudo.get_param('oxy_paie.day_start') or 1
		return fields.Date.to_string(date.today().replace(day=int(day_start)))

	def get_date_end(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_end = ICPSudo.get_param('oxy_paie.day_end')
		date_end = day_end and fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=int(day_end))).date()) or fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
		return date_end

	date_start = fields.Date(default=get_date_start)
	date_end = fields.Date(default=get_date_end)