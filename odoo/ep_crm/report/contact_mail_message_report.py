# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class ContactMailMessageReport(models.Model):
    """ Contact Mail Message Analysis """

    _name = "contact.mail.message.report"
    
    _auto = False
    _description = "Contact Mail Message Analysis"
    _rec_name = 'id'

    result_categ_id = fields.Many2one(string="Catégorie de résultat", comodel_name="activity.result.category", tracking=True)
    result_id = fields.Many2one(string="Résultat", comodel_name="activity.result", readonly=True)
    contact_id = fields.Many2one('res.partner', string='Contact', readonly=True,)
    date_deadline = fields.Date(string="Date de l'évenement", )
    date = fields.Datetime('Date', readonly=True)

    record_name = fields.Char( readonly=True)
    summary = fields.Char( readonly=True)
    user_id = fields.Many2one('res.users', readonly=True)
    subtype_id = fields.Many2one('mail.message.subtype', 'Subtype', ondelete='set null', readonly=True)
    mail_activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', readonly=True)
 
   

    def _select(self):
        return """
            SELECT
                m.id,
                m.record_name,
                m.summary,
                m.contact_id,
                m.mail_activity_type_id,
                m.date_deadline,
                m.user_id,
                m.result_categ_id,
                m.result_id,
                m.subtype_id,
                m.date
        """

    def _from(self):
        return """
            FROM mail_message AS m
        """


    def _join(self):
        return """
            JOIN res_partner AS l ON m.res_id = l.id
        """
    
    def _where(self):
        return """
            WHERE
                m.model = 'res.partner' AND m.mail_activity_type_id IS NOT NULL
        """ 

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )
