# -*- coding: utf-8 -*-

import time
from datetime import datetime
from odoo import api, models, _
from odoo.exceptions import UserError
import math
import babel
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import ustr

class wrapped_report_journal(models.AbstractModel):
	_name = 'report.oxy_paie.journal_paie'

	def get_net(self, payslips):
		total = 0
		for payslip in payslips:
			for rule in payslip.details_by_salary_rule_category:
				if rule.code == "SALNETP":
					total += rule.total
		return total

	def get_totals(self, payslips):
		somme_gain = 0
		somme_retenu = 0
		for payslip in payslips:
			for line in payslip.line_ids:
				if line.salary_rule_id.type == 'gain':
					somme_gain += line.total

				if line.salary_rule_id.type == 'retenu':
					somme_retenu += line.total
		return [somme_gain, somme_retenu]

	def get_base(self, line):
		tmp = 0
		if line.amount_select == 'percentage':
			tmp = line.amount
		elif line.code == 'R660':
			for rule in line.slip_id.line_ids:
				if rule.code in ('SIMP', 'BIMP'):
					tmp = rule.total
		elif line.code == 'R002':
			if line.contract_id.schedule_pay == 'monthly':
				if line.slip_id.calcul_reel:
					for rule in line.slip_id.line_ids:
						if rule.code in ('NHT'):
							tmp = rule.total
				else:
					tmp = 173.33
			elif line.contract_id.schedule_pay == 'horaire':
				for rule in line.slip_id.line_ids:
					if rule.code in ('NHT'):
						tmp = rule.total
			else:
				for rule in line.slip_id.line_ids:
					if rule.code in ('NJT'):
						tmp = rule.total
		elif line.code == 'SBAMJ':
			tmp = 173.33
		elif line.code == 'R260':
			sbam = 0
			mabs = 0
			for rule in line.slip_id.line_ids:
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
			if line.contract_id.schedule_pay in ('monthly'):
				return line.contract_id.taux_horaire
			else:
				for c in line.slip_id.line_ids:
					if c.code == 'TJOR':
						return c.total
		elif line.code == 'R260':
			return line.slip_id.iep_eff
		return 0

	def get_payslips(self,month_year):
		month_splited = str(month_year).split('-')
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start = ICPSudo.get_param('oxy_paie.day_start')
		day_end = ICPSudo.get_param('oxy_paie.day_end')
		if day_start:
			date = datetime.strptime(str(day_start)+'-'+str(month_year),'%d-%m-%Y')
			month = (date + relativedelta(months=-1)).month
		else:
			day_start = 1
			month = int(month_splited[0])
		day_end = day_end and day_end or calendar.monthrange(int(month_splited[1]),int(month_splited[0]))[1]
		date_from = datetime.strptime(str(day_start)+'-'+str(month)+'-'+month_splited[1],'%d-%m-%Y')
		date_to = datetime.strptime(str(day_end)+'-'+str(month_year),'%d-%m-%Y')
		payslips = self.env['hr.payslip'].search([('date_from','=',date_from),('date_to','<=',date_to),('state','=','done'),('credit_note','=',False),('avoir_payslip','=',False)])
		return payslips

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		locale = self.env.context.get('lang') or 'en_US'
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_ids', []))
		date = datetime.strptime('01-'+data['form']['month'],'%d-%m-%Y')
		month = ustr(babel.dates.format_date(date=date, format='MMMM y', locale=locale)).title()
		get_payslips = self.get_payslips(data['form']['month'])
		totals = self.get_totals(get_payslips)
		total_net = self.get_net(get_payslips)
		return {
			'doc_ids': docids,
			'doc_model': model,
			'data': data['form'],
			'docs': docs,
			'time': time,
			'company' : self.env.user.company_id,
			'month' : month,
			'base' : self.get_base,
			'taux' : self.get_taux,
			'totals' : self.get_totals,
			'net' : self.get_net,
			'get_payslips' : get_payslips,
			'total_gain' : totals[0],
			'total_retenu' : totals[1],
			'total_net' : total_net,}
