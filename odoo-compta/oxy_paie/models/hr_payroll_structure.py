# -*- encoding: utf-8 -*-
from odoo import models, api, fields, _

class hr_payroll_structure(models.Model):
	_inherit = 'hr.payroll.structure'

	retenue_mutuelle = fields.Float('Montant de la retenue mutuelle',required=True)
	conge_du = fields.Selection([('1','Janvier'),('2','Février'),('3','Mars'),('4','Avril'),('5','Mai'),('6','Juin'),('7','Juillet'),('8','Aout'),('9','Septembre'),('10','Octobre'),('11','Novembre'),('12','Décembre')])
	conge_au = fields.Selection([('1','Janvier'),('2','Février'),('3','Mars'),('4','Avril'),('5','Mai'),('6','Juin'),('7','Juillet'),('8','Août'),('9','Septembre'),('10','Octobre'),('11','Novembre'),('12','Décembre')])