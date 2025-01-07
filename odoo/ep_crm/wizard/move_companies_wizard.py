
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging


class MoveCompaniesWizard(models.TransientModel):
    _name = 'move.companies.wizard'

    target_portfolio_id = fields.Many2one('portfolio', string='Portefeuille Cible')

    def _portfolio_partners(self):
        portfolio = self.env['portfolio'].browse(self._context.get('active_ids', []))
        partner_ids = self.env['res.partner'].search([('id', 'in', portfolio.mapped('partner_ids').ids)])
        return [('id', 'in', partner_ids.ids)]

    # Get the partner_ids of the current portfolio
    partner_ids = fields.Many2many('res.partner', string='Entreprises',domain=_portfolio_partners)

    def move_companies(self):
        portfolio = self.env['portfolio'].browse(self._context.get('active_ids', []))

        for rec in self:
            for partner in rec.partner_ids:
                # Add the target_portfolio to partner portfolio_ids
                partner.update({
                    # 'portfolio_ids': [(6, 0, rec.target_portfolio_id)]
                    'portfolio_ids': [(4, rec.target_portfolio_id.id)]
                })
                # Remove the partner from the portfolio partner_ids
                portfolio.update({

                    'partner_ids': [(3, partner.id)]
                })




