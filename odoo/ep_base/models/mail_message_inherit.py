# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt
from collections import defaultdict


class MailMessageInherit(models.Model):
    _inherit = "mail.message"
    _order = 'date_deadline desc'

    result_categ_id = fields.Many2one(string="Catégorie de résultat", comodel_name="activity.result.category", tracking=True)

    result_id = fields.Many2one(string="Résultat", comodel_name="activity.result", tracking=True)

    contact_id = fields.Many2one('res.partner', string='Contact', tracking=True)

    date_deadline = fields.Date("Date d'échéance", tracking=True)

    mail_activity_type_id = fields.Many2one(
        'mail.activity.type', 'Mail Activity Type',
        index=True, ondelete='set null')

    summary = fields.Char('Résumé', tracking=True)
    # Add it in order to acces the user_id
    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, tracking=True)
    
    icone_code = fields.Html('icone_code',compute='_compute_icone_code')
    company_id = fields.Many2one(
        comodel_name='res.company', required=True,
        default=lambda self: self.env.company)
    @api.depends('mail_activity_type_id')
    def _compute_icone_code(self):
        for message in self:
            if message.mail_activity_type_id.icon:
                message.icone_code = ("<i class='fa %s'></i>")  % message.mail_activity_type_id.icon
            else:
                message.icone_code = ""

    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        self = self.with_context({'allow_group_by': True})
        return super(MailMessageInherit, self)._read_group_raw(
            domain=domain, fields=fields, groupby=groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy,
        )