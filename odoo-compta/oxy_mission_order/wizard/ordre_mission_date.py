# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ordre_mission_date(models.TransientModel):
	_name="ordre.mission.date"

	def get_date(self):
		if 'active_model' in self._context and self._context['active_model'] == 'hr.mission.order':
			return self.env['hr.mission.order'].browse(self._context['active_id']).end_date
		elif self._context['active_model'] == 'hr.mission.order.lot':
			return self.env['hr.mission.order.lot'].browse(self._context['active_id']).end_date


	date_fin = fields.Date('Date fin de la mission',default=get_date)
	demi_journee = fields.Boolean('Demi journée ?')
	type_demi_journee = fields.Selection([('matin','Matin'),('apres_midi','Après-midi')],default="matin",string="#")


	def termine(self):
		if 'active_model' in self._context and self._context['active_model'] == 'hr.mission.order':
			res = self.env['hr.mission.order'].browse(self._context['active_id'])
			if res:
				res.state = 'termine'
				res.employe_id.in_mission = False
				res.employe_id.start_date = False
				res.employe_id.end_date = False
				if not self.demi_journee:
					res.end_date = self.date_fin
					res.retour_type = 'date'
				else:
					res.retour_type = 'demi_journee'
					res.type_demi_journee = self.type_demi_journee
		elif self._context['active_model'] == 'hr.mission.order.lot':
			res = self.env['hr.mission.order.lot'].browse(self._context['active_id'])
			if res:
				res.state = 'termine'
				res.end_date = self.date_fin
				for line in res.mission_order_ids:
					line.state = 'termine'
					line.employe_id.in_mission = False
					line.employe_id.start_date = False
					line.employe_id.end_date = False
					if not self.demi_journee:
						line.end_date = self.date_fin
						line.retour_type = 'date'
					else:
						line.retour_type = 'demi_journee'
						line.type_demi_journee = self.type_demi_journee




class ordre_mission_employees(models.TransientModel):
	_name='ordre.mission.employees'

	employee_ids = fields.Many2many('hr.employee',string='Employés')


	def generer(self):
		ordre_id = self.env['hr.mission.order.lot'].browse(self._context['active_id'])
		for emp in self.employee_ids:
			self.env['hr.mission.order'].create({
					'employe_id' : emp.id,
					'mission_id' : ordre_id.mission_id.id,
					'start_date' : ordre_id.start_date,
					'end_date' : ordre_id.end_date,
					'description' : ordre_id.description and ordre_id.description or '',
					'country_id' : ordre_id.country_id and ordre_id.country_id.id or '',
					'state_id' : ordre_id.state_id and ordre_id.state_id.id or '',
					'adresse' : ordre_id.adresse and ordre_id.adresse or '',
					'lot_id' : self._context['active_id'],
					'retour_type' : ordre_id.retour_type,
					'type_demi_journee' : ordre_id.type_demi_journee,
				})