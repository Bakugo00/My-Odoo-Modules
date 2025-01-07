# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
	_inherit = 'res.company'

	day_start = fields.Char(string='Jour de début')
	day_end = fields.Char(string='Jour de fin')
	taux_panier = fields.Float('Taux panier')
	taux_transport = fields.Float('Taux transport')
	lieu_declaration_cnas = fields.Char('Lieur de declaration CNAS')
	num_cotisant = fields.Char('Numéro cotisant')