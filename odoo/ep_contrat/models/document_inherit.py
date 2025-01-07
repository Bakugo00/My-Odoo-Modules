from odoo import models,fields,api
from odoo.exceptions import UserError


class DocumentInherit(models.Model):
    _inherit = 'document'

    customer_contract_id = fields.Many2one("customer.contract",string="Réf Contrat Client",ondelete="cascade",store=True, tracking=True)
    supplier_contract_id = fields.Many2one("supplier.contract",string="Réf Contrat Fournisseur",ondelete="cascade",store=True, tracking=True)
