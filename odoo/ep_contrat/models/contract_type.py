from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class ContractType(models.Model):
    _name = 'contract.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(string='Désignation')
    active = fields.Boolean(default=True)

    type = fields.Selection([
        ('commercial', 'Commercial'),
        ('non-commercial', 'Non commercial'),
    ], string='Type')

    amount = fields.Monetary(string="Montant du contrat")

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                          default=lambda self: self.env.user.company_id.currency_id.id, required=True)

