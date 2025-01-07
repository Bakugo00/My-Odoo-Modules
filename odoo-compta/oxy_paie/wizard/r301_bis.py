# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class r301_bis(models.TransientModel):
	_name="r301.bis"

	year = fields.Selection([(str(y), str(y)) for y in range(2021, (datetime.now().year)+1 )], string='Année')

	def print_report(self):
		self.ensure_one()
		data = {}
		data['year'] = self.year
		return self.env.ref('oxy_paie.bis_report_xlsx').report_action(self, data=data)
