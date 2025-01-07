from odoo import models, fields, api
from odoo.exceptions import UserError


class DocumentInherit(models.Model):
    _inherit = 'document'

    mrp_workorder_id = fields.Many2one("mrp.workorder", string="Réf Ordre de travail", ondelete="cascade",
                                       tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Bon de Commande')
    production_id = fields.Many2one('mrp.production', string='Ordre de Production')
    employee_id = fields.Many2one('res.users', string='Employé',readonly=True)

    def create(self, vals_list):
        for vals in vals_list:
            vals['employee_id'] = self.env.user.id
        return super().create(vals_list)
