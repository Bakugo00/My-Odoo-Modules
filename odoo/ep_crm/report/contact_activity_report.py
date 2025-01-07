# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class ContactActivityReport(models.Model):
    """ Contact Activity Analysis """

    _name = "contact.activity.report"
    
    _auto = False
    _description = "Contact Activity Analysis"
    _rec_name = 'id'

    contact_id = fields.Many2one('res.partner', string='Contact', readonly=True,)
    sources = fields.Selection([
        ('other', 'Autres'),('search_eng', 'moteurs de recherche (google yahoo bing ...)'),('social_media', 'Réseaux sociaux'),
        ('link', 'Lien sur un autre site'),('press', 'par la presse '),('wom', 'Bouche à oreille ')
    ], string='Autre Source', readonly=True)
    date_deadline = fields.Date(string="Date de l'évenement", readonly=True)
    res_name = fields.Char( readonly=True)
    summary = fields.Char( readonly=True)
    user_id = fields.Many2one('res.users', readonly=True)
    note = fields.Html('Activity Description', readonly=True)
    activity_type_id = fields.Many2one('mail.activity.type', 'Activity Type', readonly=True)
 
   

    def _select(self):
        return """
            SELECT
                m.id,
                m.res_name,
                m.summary,
                m.contact_id,
                m.activity_type_id,
                m.date_deadline,
                m.user_id,
                m.note,
                m.sources
        """

    def _from(self):
        return """
            FROM mail_activity AS m
        """


    def _join(self):
        return """
            JOIN res_partner AS l ON m.res_id = l.id
        """
    
    def _where(self):
        return """
            WHERE
                m.res_model = 'res.partner' AND m.activity_type_id IS NOT NULL
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
