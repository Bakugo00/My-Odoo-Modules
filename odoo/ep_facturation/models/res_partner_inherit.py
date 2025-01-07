# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    total_unpaid_invoiced = fields.Monetary(compute='_compute_unpaid_invoiced', string="Reste à payer",
                                     groups='account.group_account_invoice,account.group_account_readonly')

    def _compute_unpaid_invoiced(self):
        self.total_unpaid_invoiced = 0

        total_unpaid_invoiced = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain_out_invoice = [
            ('partner_id', 'in', all_partner_ids),
            # ('state', 'not in', ['draft', 'cancel']),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
        ]
        domain_out_refund = [
            ('partner_id', 'in', all_partner_ids),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_refund'),
        ]
        # price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'], ['partner_id'])
        moves_out_invoice = self.env['account.move'].search(domain_out_invoice)
        moves_out_refund = self.env['account.move'].search(domain_out_refund)
        for move in moves_out_invoice:
            total_unpaid_invoiced += move.amount_residual
        # for move in moves_out_refund:
        #     total_unpaid_invoiced -= move.amount_total

        # print(total_unpaid_invoiced)

        self.total_unpaid_invoiced = total_unpaid_invoiced

    def action_view_unpaid_invoiced(self):
        # This will make sure we have on record, not multiple records.
        self.ensure_one()
        context = dict(
            create=False,
        )
        domain = [
            ('partner_id', '=', self.id),
            ('state', 'not in', ['draft', 'cancel']),
            ('move_type', 'in', ('out_refund', 'out_invoice')),
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures Impayés',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': domain,
            'context': context
        }

    # Redefine the function to remove search_default_unpaid
    def action_view_partner_invoices(self):
        # res = super(ResPartnerInherit, self).action_view_partner_invoices()
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('partner_id', 'child_of', self.id),
        ]
        action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale'}
        return action