# -*- coding: utf-8 -*-
from odoo import models, fields, api , _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError

class hr_primes(models.Model):
	_name = 'hr.primes'
	_rec_name = "primes_type_id"

	def get_period_from(self):
		tmp = []
		date = datetime.now() + relativedelta(years=-2)
		for i in range(0,36):
			tmp.append((str(date.strftime('%m'))+'-'+str(date.strftime('%Y')), str(date.strftime('%B'))+' '+str(date.strftime('%Y'))))
			date += relativedelta(months=+1)
		return tmp

	def get_period_to(self):
		tmp = []
		date = datetime.now() + relativedelta(years=-1)
		for i in range(0,36):
			tmp.append((str(date.strftime('%m'))+'-'+str(date.strftime('%Y')), str(date.strftime('%B'))+' '+str(date.strftime('%Y'))))
			date += relativedelta(months=+1)
		return tmp

	primes_type_id = fields.Many2one('hr.primes.type', string="Types prime")
	affectation = fields.Selection([('mensuel','Mensuel'),('ocasionnel','Occasionnel'),('periodique','Périodique'),('annuel','Annuel')], 'Type affectation', default="mensuel")
	hr_primes_line_ids = fields.One2many('hr.primes.lines', 'hr_primes_id',string='Employés')
	state = fields.Selection([('brouillon', 'Brouillon'), ('valide', 'Validé'), ('archiver', 'Archiver')],'Etats', default='brouillon')
	date_to = fields.Selection(lambda self : self.get_period_to(), string="au")
	date_from = fields.Selection(lambda self : self.get_period_from(), string="du")
	month = fields.Selection([('1','Janvier'),('2','Février'),('3','Mars'),('4','Avril'),('5','Mai'),('6','Juin'),('7','Juillet'),('8','Août'),('9','Septembre'),('10','Octobre'),('11','Novembre'),('12','Décembre')], 'Mois de', default="1")
	
	def valide(self):
		self.state='valide'
		for line in self.hr_primes_line_ids:
			line.state = 'valide'

	@api.model
	def archive_primes(self):
		primes = self.search([('affectation','=','periodique')])
		date = datetime.now()
		for prime in primes:
			date_to = datetime.strptime(str(date.day) + '-' + str(prime.date_to),'%d-%m-%Y')
			if date > date_to:
				prime.state = 'archiver'

				
	def unlink(self):
		for rec in self:
			if rec.state != 'brouillon':
				raise UserError(('Vous ne pouvez pas supprimer les primes validé!'))
		return super(hr_primes,self).unlink()
		
class hr_primes_lines(models.Model):
	_name = 'hr.primes.lines'

	employee_id = fields.Many2one('hr.employee', string="Employé")
	taux_montant = fields.Monetary(string='Taux/Montant')
	currency_id = fields.Many2one('res.currency',default = lambda self:self.env.user.company_id.currency_id.id)
	hr_primes_id = fields.Many2one('hr.primes', String='Affectaion primes',ondelete="cascade")
	state = fields.Selection([('brouillon', 'Brouillon'), ('valide', 'Validé'), ('archiver', 'Archiver')], string="Etats", default='brouillon')