from odoo import api, fields, models, _, tools


class ClientCategory(models.Model):
    _name = "client.category"

    name = fields.Text(string='Nom', required=True)
    remise = fields.Float(string='Remise(%)',required=True)

class Remise(models.Model):
    _name = "remise"

    name = fields.Text(string='Nom', required=True)
    remise = fields.Float(string='Remise(%)',required=True)
    date_debut = fields.Date('Date Debut')
    date_fin = fields.Date('Date Fin')
    product_ids = fields.Many2many('product.template', string='Produits')
