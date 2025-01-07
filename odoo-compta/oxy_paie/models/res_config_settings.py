# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	day_start = fields.Char(string='Jour de début')
	day_end = fields.Char(string='Jour de fin')
	taux_panier = fields.Float('Taux panier')
	taux_transport = fields.Float('Taux transport')

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		res.update(
			day_start=ICPSudo.get_param('oxy_paie.day_start'),
			day_end=ICPSudo.get_param('oxy_paie.day_end'),
			taux_panier=float(ICPSudo.get_param('oxy_paie.taux_panier')),
			taux_transport=float(ICPSudo.get_param('oxy_paie.taux_transport')),
		)
		return res

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		ICPSudo = self.env['ir.config_parameter'].sudo()
		day_start = self.day_start and self.day_start or False
		ICPSudo.set_param("oxy_paie.day_start", day_start)
		day_end = self.day_end and self.day_end or False
		ICPSudo.set_param("oxy_paie.day_end", day_end)
		taux_panier = self.taux_panier and self.taux_panier or False
		ICPSudo.set_param("oxy_paie.taux_panier", taux_panier)
		taux_transport = self.taux_transport and self.taux_transport or False
		ICPSudo.set_param("oxy_paie.taux_transport", taux_transport)