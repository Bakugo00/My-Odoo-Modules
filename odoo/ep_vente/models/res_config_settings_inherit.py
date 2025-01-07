from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_doc_quotation_customer = fields.Boolean("Bon commande client", implied_group='ep_vente.group_doc_quotation_customer')
