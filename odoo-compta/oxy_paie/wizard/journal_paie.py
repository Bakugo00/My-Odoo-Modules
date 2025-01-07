# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import babel
from datetime import datetime
from odoo.tools import ustr
from dateutil.relativedelta import relativedelta

class journal_paie(models.TransientModel):
	_name="journal.paie"

	def get_months(self):
		tmp = []
		locale = self.env.context.get('lang') or 'en_US'
		date = datetime.strptime('2022-01-01','%Y-%m-%d')
		date_now = datetime.now()
		months = (date_now.year - date.year) * 12 + (date_now.month - date.month) + 1
		for i in range(0,months):
			tmp.append((str(date.strftime('%m'))+'-'+str(date.strftime('%Y')), ustr(babel.dates.format_date(date=date, format='MMMM y', locale=locale)).title()))
			date += relativedelta(months=+1)
		return tmp

	month = fields.Selection(lambda self : self.get_months(), string='Mois', default=lambda self : (datetime.now() + relativedelta(months=-1)).strftime('%m-%Y'))

	def print_report(self):
		self.ensure_one()
		data = {}
		data['form'] = self.read(['month'])[0]
		return self.env.ref('oxy_paie.report_journal_id').report_action(self, data=data)