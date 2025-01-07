from odoo import models, fields, api


class Document(models.Model):
    _name = "document"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref_document = fields.Char(string="Réf du document", tracking=True)
    doc_classement = fields.Selection([('of_tech_type', 'Offre Technique'), ('of_fin_type', 'Offre Financiére'), ('admin_type', 'Dossier  administratif'), ('tableau', 'Tableau comparatif'), ('affaire', "Chemise d'affaire")],string="Classement dans l'offre",store=True,default='of_tech_type', tracking=True)
    name = fields.Char(string="Intitulé", tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string="Pièces jointes", tracking=True)
    datas = fields.Binary(related='attachment_id.datas', string="Contenu", tracking=True)
    # name = fields.Char(related='attachment_id.name', string="Nom")
    # datas_fname = fields.Char(related='attachment_id.datas_fname', string="Contenu")
    # directory_id = fields.Many2one("document.directory", 'Dossier')

    document = fields.Binary(string="Pièce jointe", tracking=True)
    file_name = fields.Char(string="Pièce jointe", tracking=True)
    active = fields.Boolean(default=True)

