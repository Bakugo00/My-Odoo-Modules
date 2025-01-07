#-*- coding:utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, api
from .amount_to_text_fr import amount_to_text_fr
import calendar
import babel
from odoo.tools import ustr

class report_cnas(models.AbstractModel):
	_name = "report.oxy_paie.report_cnas"

	regi_total = 0
	regi_total_globale = 0
	def get_period(self, type, month, cotisation_label):
		if type == 'periodically':
			return cotisation_label
		else:
			d1 = datetime.strptime('01-'+str(month),'%d-%m-%Y')
			locale = self.env.context.get('lang') or 'en_US'
			return ustr(babel.dates.format_date(date=d1, format='MMMM y', locale=locale)).title()

	def sum_total(self):
		return self.regi_total + self.regi_total_globale
	
	def _get_information(self, company):
		return self.env['res.company'].browse(company[0])

	def get_currency(self, company):
		return self.env['res.company'].browse(company[0]).currency_id

	def _get_date(self):
		locale = self.env.context.get('lang') or 'en_US'
		d1 = datetime.now().date()
		return ustr(babel.dates.format_date(date=d1, format='MMMM y', locale=locale)).title()

	def get_dates(self, month_year, month_au, type):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start = ICPSudo.get_param('oxy_paie.day_start')
		day_end = ICPSudo.get_param('oxy_paie.day_end')
		month_splited = str(month_year).split('-')
		if day_start:
			date = datetime.strptime(str(day_start)+'-'+str(month_year),'%d-%m-%Y')
			month = (date + relativedelta(months=-1)).month
		else:
			day_start = 1
			month = int(month_splited[0])
		date_from = datetime.strptime(str(day_start)+'-'+str(month)+'-'+str(month_splited[1]), '%d-%m-%Y')
		if type == 'periodically':
			month_splited = str(month_au).split('-')
			month_year = month_au
		day_end = day_end and day_end or calendar.monthrange(int(month_splited[1]),int(month_splited[0]))[1]
		date_to = datetime.strptime(str(day_end)+'-'+str(month_year),'%d-%m-%Y')
		return date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')

	def get_amount(self, month, month_au, type, taux, taux_globale):
		date_from, date_to = self.get_dates(month, month_au, type)
		payslip_obj = self.env['hr.payslip']
		payslip_line = self.env['hr.payslip.line']
		payslip_lines = []
		res = []
		regi_total_tmp = 0
		self.env.cr.execute("SELECT pl.id from hr_payslip_line as pl "\
						"LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id) "\
						"WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "\
						"AND hp.state = 'done' "\
						"ORDER BY pl.slip_id, pl.sequence",
						(date_from, date_to))
		payslip_lines = [x[0] for x in self.env.cr.fetchall()]
		for line in payslip_line.browse(payslip_lines):
			res.append({
				'payslip_name': line.slip_id.name,
				'name': line.employee_id.name,
				'code_emp': line.employee_id.matricule,
				'code' : line.code,
				'abattement': line.contract_id.abattement,
				'amount': line.amount,
				'total': line.total,
			})
			if line.contract_id.abattement.taux == taux:
				if line.code == 'SPOST':
					regi_total_tmp += (line.total * taux_globale)/100#34.5
					#self.regi_total += (line.total * taux_globale)/100
		return regi_total_tmp

	def get_assiette(self, month, month_au, type, taux):
		date_from, date_to = self.get_dates(month, month_au, type)
		payslip_line = self.env['hr.payslip.line']
		payslip_lines = []
		res = []
		total = 0.0
		self.env.cr.execute("SELECT pl.id from hr_payslip_line as pl "\
						"LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id) "\
						"WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "\
						"AND hp.state = 'done' "\
						"ORDER BY pl.slip_id, pl.sequence",
						(date_from, date_to))
		payslip_lines = [x[0] for x in self.env.cr.fetchall()]
		for line in payslip_line.browse(payslip_lines):
			res.append({
				'payslip_name': line.slip_id.name,
				'name': line.employee_id.name,
				'code_emp': line.employee_id.matricule,
				'code' : line.code,
				'abattement': line.contract_id.abattement,
				'amount': line.amount,
				'total': line.total,    
			})
			if line.contract_id.abattement.taux == taux:
				if line.code == 'SPOST':
					total += line.total
		return total

	def get_assiette_globale(self, month, month_au, type):
		date_from, date_to = self.get_dates(month, month_au, type)
		payslip_obj = self.env['hr.payslip']
		payslip_line = self.env['hr.payslip.line']
		payslip_lines = []
		res = []
		total = 0
		self.env.cr.execute("SELECT pl.id from hr_payslip_line as pl "\
						"LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id) "\
						"WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "\
						"AND hp.state = 'done' "\
						"ORDER BY pl.slip_id, pl.sequence",
						(date_from, date_to))
		payslip_lines = [x[0] for x in self.env.cr.fetchall()]
		for line in payslip_line.browse(payslip_lines):
			res.append({
				'payslip_name': line.slip_id.name,
				'name': line.employee_id.name,
				'code_emp': line.employee_id.matricule,
				'code' : line.code,
				'abattement': line.contract_id.abattement,
				'amount': line.amount,
				'total': line.total,    
			})
			if line.contract_id.abattement.taux in (0, 10, 20):
				if line.code == 'SPOST':
					total += line.total
		return total

	def get_amount_globale(self, month, month_au, type):
		date_from, date_to = self.get_dates(month, month_au, type)
		payslip_obj = self.env['hr.payslip']
		payslip_line = self.env['hr.payslip.line']
		payslip_lines = []
		res = []
		regi_total_globale_tmp = 0.0
		self.env.cr.execute("SELECT pl.id from hr_payslip_line as pl "\
						"LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id) "\
						"WHERE (hp.date_from >= %s) AND (hp.date_to <= %s) "\
						"AND hp.state = 'done' "\
						"ORDER BY pl.slip_id, pl.sequence",
						(date_from, date_to))
		payslip_lines = [x[0] for x in self.env.cr.fetchall()]
		for line in payslip_line.browse(payslip_lines):
			res.append({
				'payslip_name': line.slip_id.name,
				'name': line.employee_id.name,
				'code_emp': line.employee_id.matricule,
				'code' : line.code,
				'abattement': line.contract_id.abattement,
				'amount': line.amount,
				'total': line.total,
				
			})
			if line.contract_id.abattement.taux in (0, 10, 20):
				if line.code == 'SPOST':
					regi_total_globale_tmp += (line.total * 0.5)/100
					#self.regi_total_globale += (line.total * 0.5)/100
		return regi_total_globale_tmp

	def _emp_entree(self, month, month_au, type):
		date_from, date_to = self.get_dates(month, month_au, type)
		d_from = datetime.strptime(date_from,'%Y-%m-%d').date()
		d_to = datetime.strptime(date_to,'%Y-%m-%d').date()
		contract = self.env['hr.contract']
		nb=0
		contrat_id = contract.search([('state','=','open')])
		for e in contrat_id:
			date_start = e.date_start
			if date_start >= d_from and date_start <= d_to:
				nb += 1
		return nb

	def _emp_sortie(self, month, month_au, type):
		date_from, date_to = self.get_dates(month, month_au, type)
		d_from = datetime.strptime(date_from,'%Y-%m-%d').date()
		d_to = datetime.strptime(date_to,'%Y-%m-%d').date()
		contract = self.env['hr.contract']
		nb=0
		contrat_id = contract.search([('state','=','open')])
		for e in contrat_id:
				if e.employee_id.non_actif == True:
					date_sortie = e.employee_id.date_sortie
					if date_sortie >= d_from and date_sortie <= d_to:
						nb += 1
		return nb

	def _effectif_total(self, month, month_au, type):
		date_from, date_to = self.get_dates(month, month_au, type)
		d_to = datetime.strptime(date_to,'%Y-%m-%d').date()
		contract = self.env['hr.contract']
		nb=0
		contract_id = contract.search([('state','=','open')])
		for e in contract_id:
			if e.employee_id.non_actif:
				date_sortie = e.employee_id.date_sortie
				if date_sortie > d_to:# and e.employee_id.affectation.id == affectation[0]:
					nb += 1
			else:
				nb += 1
		return nb

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		return {
			'doc_ids': docids,
			'data': data,
			'get_amount' : self.get_amount,
			'get_amount_globale' : self.get_amount_globale,
			'sum_total': self.sum_total,
			'emp_entree' : self._emp_entree,
			'emp_sortie' : self._emp_sortie,
			'effectif_total' : self._effectif_total,
			'get_assiette': self.get_assiette,
			'get_assiette_globale' : self.get_assiette_globale,
			'get_date' : self._get_date,
			'get_information' : self._get_information,
			'get_currency' : self.get_currency,
			'amount_to_text_fr' : amount_to_text_fr,
			'get_period' : self.get_period,
			}