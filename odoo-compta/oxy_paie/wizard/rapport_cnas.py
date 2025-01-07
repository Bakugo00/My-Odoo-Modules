# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import babel
from odoo.tools import ustr

class rapport_cnas(models.TransientModel):
	_name="rapport.cnas"

	def get_months(self):
		tmp = []
		locale = self.env.context.get('lang') or 'en_US'
		date = datetime.strptime('2021-01-01','%Y-%m-%d')
		date_now = datetime.now()
		months = (date_now.year - date.year) * 12 + (date_now.month - date.month) + 1
		for i in range(0,months):
			tmp.append((str(date.strftime('%m'))+'-'+str(date.strftime('%Y')), ustr(babel.dates.format_date(date=date, format='MMMM y', locale=locale)).title()))
			date += relativedelta(months=+1)
		return tmp

	month = fields.Selection(lambda self : self.get_months(), string='Mois', default=lambda self : (datetime.now() + relativedelta(months=-1)).strftime('%m-%Y'),required=True)
	month_to = fields.Selection(lambda self : self.get_months(), string='Mois au')
	type_cotisation = fields.Selection([('monthly','Par mois'),('periodically','Par période')],default='monthly')
	company_id = fields.Many2one('res.company',default=lambda self : self.env.user.company_id)
	cotisation_label = fields.Char('Période de cotisation')
	
	def print_report(self):
		self.ensure_one()
		data = {}
		data['form'] = self.read(['month', 'month_to', 'company_id', 'type_cotisation', 'cotisation_label'])[0]
		return self.env.ref('oxy_paie.report_cnas_id').report_action(self, data=data)