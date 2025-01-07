# -*- encoding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, api, fields, _
from odoo.exceptions import Warning, ValidationError

class hr_prets(models.Model):
	_name = 'hr.prets'
	_rec_name="complete_name"


	complete_name = fields.Char(compute="get_complete_name")
	employee_id = fields.Many2one('hr.employee','Employé',required=True)
	date = fields.Date('Date de prêts',required=True, default=lambda self:datetime.now())
	montant = fields.Monetary('Montant',required=True)
	tranche = fields.Monetary('Tranche')
	nb_mois = fields.Integer('Nombre de retenus',required=True, default=1)
	reste = fields.Monetary('Reste',compute='get_reste',store=True)
	state = fields.Selection([('draft','Brouillon'),('done','Valider'),('payee','Rembourser')],
		'Etat', default='draft')
	pret_lines = fields.One2many('hr.prets.lines','prets_id','')
	date_remb = fields.Date('Date de début de remboursement',required = True)
	currency_id = fields.Many2one('res.currency',default=lambda self:self.env.user.company_id.currency_id)


	@api.depends('employee_id','reste')
	def get_complete_name(self):
		for pret in self:
			employee = str(pret.employee_id.name)
			if pret.employee_id.prenom:
				employee += ' ' + str(pret.employee_id.prenom)
			pret.complete_name = "Prêt pour : " + employee + "(Reste : " + str(pret.reste)+ ")"

	@api.depends('montant','pret_lines','pret_lines.state')
	def get_reste(self):
		for pret in self:
			rembourse = 0
			new = True
			for line in pret.pret_lines:
				if line.state == 'attente':
					rembourse += line.montant
				else:
					new = False
			if new:
				pret.reste = pret.montant
			else:
				pret.reste = rembourse


	def valider(self):
		return self.write({'state' : 'done'})

	def reporter(self):
		for line in self.pret_lines:
			if line.state == 'attente':
				date = line.date + relativedelta.relativedelta(months=1)
				line.write({'date' : date})

	def calculer(self):
		self.pret_lines.unlink()
		date_prets = datetime.strptime(datetime.strftime(self.date_remb,'%Y-%m-%d'),'%Y-%m-%d')
		data = {}
		tranche = self.montant / self.nb_mois
		str_date = str(date_prets.year)+"-"+str(date_prets.month) + "-01"
		date_prets = datetime.strptime(str_date,'%Y-%m-%d')
		for i in range(0, self.nb_mois):
			data = {
				'date' : date_prets,
				'state' : 'attente',
				'montant' : tranche,
				'prets_id' : self.id
			}
			self.env['hr.prets.lines'].create(data)
			date_prets += relativedelta.relativedelta(months=1) 
		return True

	
	def unlink(self):
		for rec in self:
			if rec.state != 'draft':
				raise ValidationError('Vous ne pouvez pas supprimer des données valider')
		return super(hr_prets,self).unlink()

class hr_prets_lines(models.Model):
	_name = 'hr.prets.lines'

	date = fields.Date('Date')
	state = fields.Selection([('attente','Attente'),('rembourser','Rembourser')],'Etat')
	montant = fields.Monetary('Montant à rembourser')
	prets_id = fields.Many2one('hr.prets',ondelete="cascade")
	currency_id = fields.Many2one('res.currency',related='prets_id.currency_id')