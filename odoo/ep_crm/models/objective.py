from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime as dt

import logging
_logger = logging.getLogger(__name__)


class Objective(models.Model):
    _name = "objective"
    _description = "Objectif"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    # _rec_name = 'name'

    READONLY_STATES = {
        'realized': [('readonly', True)],
    }

    name = fields.Char(string='Numéro', tracking=True, readonly=True)

    active = fields.Boolean(default=True)

    comment = fields.Text(string='Commentaire', tracking=True)

    type_id = fields.Many2one('objective.type', string='Type', tracking=True)

    user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)

    objective = fields.Float(string="Objectif", tracking=True)

    progress = fields.Float(string="Réalisation", default=0, tracking=True, compute='_compute_progress', store=True, readonly=True)

    start_date = fields.Date(string="Date début", tracking=True)

    end_date = fields.Date(string="Date fin", tracking=True)

    state = fields.Selection(selection=[
        ('draft', 'Planifié'),
        ('in progress', 'En cours'),
        ('realized', 'Réalisé'),
    ], string='Statut', required=True, readonly=True, copy=False, tracking=True,
        default='draft', compute='_compute_state')

    type = fields.Selection([('turnover', "Chiffre d'affaires"),
                             ('sale_order_amount', 'Bons de commande'),
                             ('payment_amount', 'Recouvrement'),
                             ('sale_order_count', 'Devis'),
                             ('appointment_count', 'Rendez-vous'),
                             ('calls_count', 'Appels'),
                             ], string='Type', tracking=True)

    @api.model
    def create(self, vals):
        """
        Add specific sequence for each type of Objectif
        :param vals:
        """
        # seq = self.env['ir.sequence'].next_by_code('objectif.seq') or '_(New)'
        seq = self.env['ir.sequence'].next_by_code('objectif.seq')
        # Affect sequence for Contract Purchase
        vals['name'] = seq
        return super(Objective, self).create(vals)

    def to_progress(self):
        for record in self:
            record.write({'state': 'in progress'})

    def to_realized(self):
        for record in self:
            record.write({'state': 'realized'})

    @api.depends('progress')
    def _compute_state(self):
        for record in self:
            if record.progress == 0:
                record.state = 'draft'
            else:
                if record.progress >= 100:
                    record.state = 'realized'
                    # record.write({'state': 'realized'})
                else:
                    record.state = 'in progress'

    # @api.depends('user_id.attendees_ids.amount_participant', 'user_id.attendees_ids')
    @api.depends('type', 'objective', 'user_id', 'start_date', 'end_date')
    def _compute_progress(self):
        """
        This function calculate the progress value for each objective type according to different parameters
        @rtype: object
        """
        for record in self:
            total = 0
            if record.type == 'turnover':
                total_out_invoice = 0
                total_out_refund = 0
                domain_out_invoice = [
                    ('invoice_user_id', '=', record.user_id.id),
                    ('state', '=', 'posted'),
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date', '>=', record.start_date),
                    ('invoice_date', '<=', record.end_date),
                ]
                total_out_invoice = sum(self.env['account.move'].search(domain_out_invoice).mapped('amount_untaxed'))
                domain_out_refund = [
                    ('invoice_user_id', '=', record.user_id.id),
                    ('state', '=', 'posted'),
                    ('move_type', '=', 'out_refund'),
                    ('invoice_date', '>=', record.start_date),
                    ('invoice_date', '<=', record.end_date),
                ]
                total_out_refund = sum(self.env['account.move'].search(domain_out_refund).mapped('amount_untaxed'))
                # Calculate the difference between invoice and refund
                total = total_out_invoice - total_out_refund
                # print('Montant chiffre affaire',total)
            if record.type == 'sale_order_amount':
                domain = [
                    ('user_id', '=', record.user_id.id),
                    ('state', '=', 'sale'),
                    ('date_order','>=', record.start_date),
                    ('date_order','<=', record.end_date),
                ]
                # Calculate the total of participant amounts
                total = sum(self.env['sale.attendees'].search(domain).mapped('amount_participant'))
                # print("Montnat bon de commandes", total)
            if record.type == 'payment_amount':
                domain_move = [
                    ('invoice_user_id', '=', record.user_id.id),
                    ('state', '=', 'posted'),
                ]
                moves = self.env['account.move'].search(domain_move)
                domain_payment = [
                    ('date','>=', record.start_date),
                    ('date','<=', record.end_date),
                    ('move_id', 'in', moves.ids),
                    ('state', '=', 'posted'),
                ]
                total = sum(self.env['account.payment'].search(domain_payment).mapped('amount'))
                # print('Montants payés', total)
            if record.type == 'sale_order_count':
                domain = [
                    ('user_id', '=', record.user_id.id),
                    ('state', '=', 'sale'),
                    ('date_order','>=', record.start_date),
                    ('date_order','<=', record.end_date),
                ]
                # count = len(self.env['sale.order'].search(domain))
                # Calculate the number of sale_order
                total = self.env['sale.attendees'].search_count(domain)
                # print("Nombre de devis", total)
            if record.type == 'appointment_count':
                domain_message = [
                  ('date','>=', record.start_date),
                  ('date','<=', record.end_date),
                  ('user_id', '=', record.user_id.id),
                  ('subtype_id', '=',  self.env.ref('mail.mt_activities').id),   # Domain to retrieve activities only
                  ('mail_activity_type_id', '=',  self.env.ref('mail.mail_activity_data_meeting').id),   # Domain to retrieve Meetings only
                ]
                total = self.env['mail.message'].search_count(domain_message)
            if record.type == 'calls_count':
                domain_message = [
                    ('date', '>=', record.start_date),
                    ('date', '<=', record.end_date),
                    ('user_id', '=', record.user_id.id),
                    ('subtype_id', '=', self.env.ref('mail.mt_activities').id),
                    # Domain to retrieve activities only
                    ('mail_activity_type_id', '=', self.env.ref('mail.mail_activity_data_call').id),
                    # Domain to retrieve Calls only
                ]
                total = self.env['mail.message'].search_count(domain_message)

            # Calculate the progress
            if record.objective and record.objective != 0:
                progress = (total / record.objective) * 100
                record.progress = progress
            else:
                record.progress = 0
            # print("--- % Progress ---", record.progress)

    def _compute_progress_cron(self):
        objective = self.env['objective'].search([])
        objective._compute_progress()
