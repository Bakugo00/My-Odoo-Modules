# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil import relativedelta

class MissionOrder(models.Model):
	_name = 'hr.mission.order'
	_order = "id desc"
	_rec_name = "employe_id"

	def get_default_country(self):
		return self.env['res.country'].search([('currency_id','=','DZD')])

	name = fields.Char(string="Référence", default="Nouvelle ordre de mission")
	employe_id = fields.Many2one('hr.employee',string="Employé", required=True)
	partner_id = fields.Many2one('res.partner',string="Partenaire")
	
	mission_id = fields.Many2one('hr.mission.object',string="Objet de la mission", required=True)
	start_date = fields.Date(string='Date de départ', required=True)
	end_date = fields.Date(string='Date de retour')
	retour_type = fields.Selection([('demi_journee','Demi journée'),('date','Entrer une date de retour')],'',default='date')
	type_demi_journee = fields.Selection([('matin','Matin'),('apres_midi','Après-midi')],default="matin",string="#")
	duration = fields.Char(string="Durée", compute="compute_duration")
	state = fields.Selection([
			('brouillon', 'Brouillon'),
			('valide', 'Validée'),
			('annule', 'Annulée')], string='État', default='brouillon')
	description = fields.Text(string='Description')
	country_id = fields.Many2one('res.country',string="Pays", default=get_default_country)
	state_id = fields.Many2one('res.country.state',string="Ville")
	adresse = fields.Char(string="Adresse")
	lot_id = fields.Many2one('hr.mission.order.lot',ondelete='cascade')
	
	company_id = fields.Many2one('res.company',default=lambda self:self.env.user.company_id.id)
	moyen_trans = fields.Selection([('tous_moy', 'Tous les moyens'),
									('taxi', 'TAXI'),
								   ('service','Véhicule de service'), 
								   ('avion', 'Avion'),
								   ('autre', 'Autre'),], 'Moyen de transport' )

	@api.depends('employe_id')
	def get_heure(self):
		for rec in self:
			rec.heure_entre = rec.employe_id.resource_calendar_id.heure_entre
			rec.heure_sortie = rec.employe_id.resource_calendar_id.heure_sortie


	heure_entre = fields.Float('heure entre',compute="get_heure",store=True)
	heure_sortie = fields.Float('heure sortie',compute="get_heure",store=True)


	@api.constrains('start_date','end_date')
	def check_dates(self):
		if self.end_date and self.end_date < self.start_date:
			raise ValidationError("Date de fin ne peut pas être avant la date de début de l'ordre de mission.")

	@api.depends('start_date','end_date')
	def compute_duration(self):
		for res in self:
			res.duration = '0'
			if res.retour_type != "demi_journee":
				if res.start_date and res.end_date:
					res.duration = str((res.end_date - res.start_date).days) + " Jour(s)"
			elif res.retour_type == 'demi_journee' and res.start_date:
				res.duration = '0.5 Jour(s)'


	def action_valider(self):
		order_ids = self.search([('employe_id','=',self.employe_id.id),('start_date','<=',self.start_date),('end_date','>=',self.start_date),('state','=','valide')])
		if order_ids:
			raise ValidationError("Cet employé(e) est déja en mission")			

		if self.retour_type == "date":
			date = self.start_date
			date_fin = self.end_date
			while date < date_fin:
				holiday_ids = self.env['hr.leave'].search([('state','=','validate'),('employee_id','=',self.employe_id.id),('date_from','<=',date.strftime('%Y-%m-%d')),('date_to','>=',date.strftime('%Y-%m-%d'))])
				if holiday_ids:
					raise ValidationError("Cet employé(e) est en congé")				
					break
				date += relativedelta.relativedelta(days=+1)

		self.name = self.env['ir.sequence'].next_by_code('hr.mission.order')
		self.state = 'valide'
		self.employe_id.in_mission = True
		self.employe_id.start_date = self.start_date
		self.employe_id.end_date = self.end_date


	def unlink(self):
		for record in self:
			if record.state != 'brouillon':
				raise ValidationError("Vous ne pouvez pas supprimer des données validé")
		return super(MissionOrder,self).unlink()


class MissionOrderLot(models.Model):
	_name = 'hr.mission.order.lot'


	def get_default_country(self):
		return self.env['res.country'].search([('currency_id','=','DZD')])


	name = fields.Char('Nom')
	start_date = fields.Date('Date début')
	end_date = fields.Date('Date fin')
	retour_type = fields.Selection([('demi_journee','Demi journée'),('date','Entrer une date de retour')],'',default='date')
	type_demi_journee = fields.Selection([('matin','Matin'),('apres_midi','Après-midi')],default="matin",string="#")
	mission_id = fields.Many2one('hr.mission.object',string="Objet de la mission")
	state = fields.Selection([
			('brouillon', 'Brouillon'),
			('valide', 'Validée'),
			('annule', 'Annulée')], string='État', default='brouillon')

	description = fields.Text(string='Description')
	country_id = fields.Many2one('res.country',string="Pays", default=get_default_country)
	state_id = fields.Many2one('res.country.state',string="Ville")
	adresse = fields.Char(string="Adresse")
	mission_order_ids = fields.One2many('hr.mission.order','lot_id',string='Ordre missions')
	description = fields.Text(string='Description')


	def action_valider(self):
		for line in self.mission_order_ids:
			line.action_valider()
		self.state = 'valide'


	def unlink(self):
		for record in self:
			if record.state != 'brouillon':
				raise ValidationError("Vous ne pouvez pas supprimer des données validé")
		return super(MissionOrderLot,self).unlink()