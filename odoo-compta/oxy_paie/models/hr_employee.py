# -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_employee(models.Model):
	_inherit = 'hr.employee'
	_rec_name = "complete_name"
	
	prenom = fields.Char(String='Prénom')
	matricule_cnas = fields.Char(String='Matricule CNAS')
	matricule = fields.Char(String='Matricule')
	type_paiement = fields.Selection([('espece', 'Espèces'), ('cheque', 'Chèques'), ('virement', 'Virement')],'Type de paiement', default='espece')
	compte = fields.Char('N° de compte bancaire')
	hors_societe =  fields.Float(string='I.A. hors société (%)')
	date_entree = fields.Date(string='Date d\'entrée')
	motif = fields.Text(String='Motif de sortie')
	date_sortie = fields.Date(string='Date de Sortie')
	non_actif = fields.Boolean('Non actif', default=False)
	complete_name = fields.Char(compute="get_complete_name", store=True)

	@api.depends('name', 'prenom')
	def get_complete_name(self):
		for record in self:
			name = record.name
			if record.prenom:
				name += ' ' + record.prenom
			record.complete_name = name