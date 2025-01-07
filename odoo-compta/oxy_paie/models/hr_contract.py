# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_contract(models.Model):
	_inherit = 'hr.contract'

	def get_taux_panier(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		taux_panier = ICPSudo.get_param('oxy_paie.taux_panier') and ICPSudo.get_param('oxy_paie.taux_panier') or 0
		return float(taux_panier)

	def get_taux_transport(self):
		ICPSudo = self.env['ir.config_parameter'].sudo()
		taux_transport = ICPSudo.get_param('oxy_paie.taux_transport') and ICPSudo.get_param('oxy_paie.taux_transport') or 0
		return float(taux_transport)

	name = fields.Char(required=False)
	taux_horaire = fields.Monetary(string="Taux Horaire")
	taux_journalier = fields.Monetary(string="Taux Journalier")
	nbr_hr_par_jr = fields.Float(string="Nombre d'heure par jour")
	nbr_hr_mois_moyen = fields.Float(string="Nombre d'heure du mois moyen",default=173.33)
	panier = fields.Boolean(string="Panier")
	indemnite_panier = fields.Float(string="Indemnité de panier",default=get_taux_panier)
	transport = fields.Boolean('Indemnité de transport')
	indemnite_transport = fields.Float('Indemnité de transport',default=get_taux_transport)
	abattement = fields.Many2one('hr.abattement', string="Abattements CNAS")
	isIep = fields.Boolean('Ancienneté')
	valeur_iep = fields.Many2one('bareme.anciennete','Valeur')

	@api.onchange('wage','nbr_hr_par_jr','nbr_hr_mois_moyen')
	def on_change_wage(self):
		if self.nbr_hr_mois_moyen != 0:
			self.taux_horaire = self.wage / self.nbr_hr_mois_moyen
		if self.nbr_hr_par_jr != 0:
			self.taux_journalier = self.taux_horaire * self.nbr_hr_par_jr

	@api.onchange('resource_calendar_id','resource_calendar_id.hours_per_day')
	def on_change_hours_per_day(self):
		self.nbr_hr_par_jr = self.resource_calendar_id.hours_per_day

	@api.model
	def create(self, vals):
		if 'name' not in vals or not vals['name']:
			vals['name'] = self.env['ir.sequence'].next_by_code('seq.contract')
		return super(hr_contract,self).create(vals)