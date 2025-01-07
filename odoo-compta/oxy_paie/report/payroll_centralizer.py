# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import ustr
from dateutil.relativedelta import relativedelta
import babel
import calendar
from .amount_to_text_fr import amount_to_text_fr

class payroll_centralizer(models.AbstractModel):
	_name = 'report.oxy_paie.payroll_centralizer_template_id'

	def get_dates(self, month_year):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start_config = ICPSudo.get_param('oxy_paie.day_start')
		day_end_config = ICPSudo.get_param('oxy_paie.day_end')
		day_start = day_start_config and day_start_config or 1
		month_splited = str(month_year).split('-')
		day_end = day_end_config and day_end_config or calendar.monthrange(int(month_splited[1]),int(month_splited[0]))[1]
		date_end = datetime.strptime(str(int(month_splited[1]))+'-'+str(int(month_splited[0]))+'-'+str(day_end),'%Y-%m-%d').date()
		date_start = datetime.strptime(str(int(month_splited[1]))+'-'+str(int(month_splited[0]))+'-'+str(day_start),'%Y-%m-%d').date()
		if day_start != 1:
			date_start += relativedelta(months=-1)
		return date_start, date_end

	def get_rubriques(self, month):
		date_from, date_to = self.get_dates(month)
		payslip_lines = self.env['hr.payslip.line'].search([('slip_id.state','=','done'), ('slip_id.date_from','=',date_from.strftime('%Y-%m-%d')),('slip_id.date_to','<=',date_to.strftime('%Y-%m-%d')),('slip_id.credit_note','=',False),('slip_id.have_credit_note','=',False),('salary_rule_id.appears_on_payslip','=',True)])
		payslip_codes = []
		for line in payslip_lines:
			payslip_codes.append(line.code)
		payslip_codes += ['SPOST', 'R015', 'SIMP', 'SALNETP']
		payslip_codes = set(payslip_codes)
		res = []
		total_gain = 0
		total_retenu = 0
		nb_travailleur = 0
		net = 0
		for code in payslip_codes:
			lines = self.env['hr.payslip.line'].search([('slip_id.state','=','done'), ('slip_id.date_from','=',date_from.strftime('%Y-%m-%d')),('slip_id.date_to','<=',date_to.strftime('%Y-%m-%d')),('slip_id.credit_note','=',False),('slip_id.have_credit_note','=',False),('code','=',code)])
			somme = sum(line.total for line in lines)
			quantity = sum(line.quantity for line in lines)
			amount = sum(line.amount for line in lines)
			eff = len(lines)
			nb_travailleur = max(nb_travailleur, eff)
			rubrique = self.env['hr.salary.rule'].search([('code','=',code)],limit=1)
			name = ''
			base = -1
			if rubrique:
				name = rubrique.name
				sequence = rubrique.sequence
				if rubrique.type == 'gain':
					type = 'gain'
					total_gain += somme
				elif rubrique.type == 'retenu':
					type = 'retenu'
					base = quantity
					if code in ('R510'):
						base = amount
					elif code == 'R660':
						simp = self.env['hr.payslip.line'].search([('slip_id.state','=','done'), ('slip_id.date_from','=',date_from.strftime('%Y-%m-%d')),('slip_id.date_to','<=',date_to.strftime('%Y-%m-%d')),('slip_id.credit_note','=',False),('slip_id.have_credit_note','=',False),('code','=','SIMP')])
						base = sum(line.total for line in simp)
					total_retenu += somme
				elif code == 'SALNETP':
					type = 'gain'
					total_gain += somme
					net = somme
				elif not rubrique.type:
					type = 'base'
			res.append({
				'code' : code,
				'name' : name,
				'type' : type,
				'base' : base,
				'somme' : somme,
				'eff' : eff,
				'sequence' : sequence,
			})
		return nb_travailleur, sorted(res, key = lambda k : k['sequence']), total_gain, total_retenu, net

	def get_company(self):
		return self.env.user.company_id

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		model = self.env.context.get('active_model')
		locale = self.env.context.get('lang') or 'en_US'
		docs = self.env[model].browse(self.env.context.get('active_ids', []))
		d1 = datetime.strptime('01-' + data['form']['month'], '%d-%m-%Y')
		date = ustr(babel.dates.format_date(date=d1, format='MMMM y', locale=locale)).title()

		return {
			'doc_ids': docids,
			'doc_model': model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'company':self.get_company(),
			'date':date,
			'get_rubriques' : self.get_rubriques,
			'amount_to_text_fr' : amount_to_text_fr,
		}