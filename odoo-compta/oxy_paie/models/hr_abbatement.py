# -*- encoding: utf-8 -*-

from odoo import models,api,fields

class hr_abattement(models.Model):
	_name = 'hr.abattement'


	name = fields.Char('description', required=True)
	code = fields.Char('Code')
	taux = fields.Float('Taux')