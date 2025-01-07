# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _

class bareme_anciennete(models.Model):
	_name = "bareme.anciennete"

	name = fields.Char('Nom', required=True)
	pourcentage = fields.Integer('Pourcentage')
	marge = fields.Integer('Tous les (Ans)')