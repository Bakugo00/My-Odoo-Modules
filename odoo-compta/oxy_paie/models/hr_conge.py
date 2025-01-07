# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class hr_conge(models.Model):
	_name = "hr.conge"

	employee_id = fields.Many2one('hr.employee',string="Employé")
	year = fields.Char('Année',size=4)
	ica = fields.Monetary('ICA',help='Indemnité de congé annuel')
	nb_jour = fields.Float('# de jours')
	currency_id = fields.Many2one('res.currency',default=lambda self:self.env.user.company_id.currency_id.id)
	ica_restant = fields.Monetary('ICA restant',help='Cumul de l\'indemnité de congé annuel restante a consommer')
	ica_stc = fields.Monetary('ICA STC')
	nb_jour_restant = fields.Float('# de jours restant',help='Nombre de jours de congé annuel restante a consommer')
	nb_jour_stc = fields.Float('# de jours restant STC')
	