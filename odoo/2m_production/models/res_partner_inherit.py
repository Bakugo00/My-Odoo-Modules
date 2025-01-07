# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    unpaid_amount_authorized = fields.Monetary(string="Montant impayé autorisé", default=0)
    # groups='account.group_account_invoice,account.group_account_readonly'

    customer_type = fields.Selection(string='Type de client', selection=[('end_customer', 'Client Final'),
                                                                         ('reseller', 'Revendeur')])
    categorie_client_id = fields.Many2one('client.category', string='Catégorie Client')

