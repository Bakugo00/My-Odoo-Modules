from odoo import api, fields, models, _, tools


class Dimesnion(models.Model):
    _name = "dimension"

    name = fields.Text(string='Nom', required=True, tracking=True)

    height = fields.Float(string='Longueur',required=True)
    width = fields.Float(string='Largeur',required=True)
