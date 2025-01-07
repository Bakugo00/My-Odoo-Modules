from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date


class SupplierContract(models.Model):
    _name = 'supplier.contract'
    _description = 'Contrat Fournisseur'
    _inherit = ['customer.contract', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    @api.model
    def create(self, vals):
        """
        Add specific sequence for each type of Contract
        :param vals:
        """
        seq = self.env['ir.sequence'].next_by_code('supplier.contract.sequence') or '_(New)'
        # affect sequence for Contract
        vals['name'] = seq
        return super(SupplierContract, self).create(vals)

