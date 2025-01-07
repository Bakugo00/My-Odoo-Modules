import itertools

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MRPRoutingWorkcenterInherit(models.Model):
    _inherit = "mrp.routing.workcenter"

    @api.constrains('sequence')
    def check_sequence(self):
        for rec in self:
            sequences = self.env["mrp.routing.workcenter"].search([('sequence', 'in', (1, 2, 3, 4))]).mapped('sequence')

            if rec.sequence in sequences:
                raise UserError(_('Cette séquence existe déja'))
