
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ConfigTimbre(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'config.timbre'
    _description = 'Fiscal Timbre configuration'

    name = fields.Char('Nom', required=True)
    valeur = fields.Float('Valeur du timbre', required=True, track_visibility='always')
    tranche = fields.Float('Tranche', required=True, track_visibility='always')
    min_value = fields.Float('Valeur Minimum', required=True, track_visibility='always')
    max_value = fields.Float('Plafond', required=True, track_visibility='always')

    account_id = fields.Many2one('account.account',"Compte De Droit d’enregistrement (Timbre) Vente",required=False, track_visibility='always')
    account_id_purchase = fields.Many2one('account.account',"Compte De Droit d’enregistrement (Timbre) Achat",required=False, track_visibility='always')
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'name must be unique per Company!'),
    ]

    @api.model
    def _timbre(self, montant):
        res = {}
        timbre_obj = self.env['config.timbre']
        liste_obj  = timbre_obj.search([])
        if not liste_obj :
           raise UserError(_('Pas de configuration du calcul Timbre.'))
        dict = liste_obj[-1]
        montant_avec_timbre = int((montant * dict['valeur']) / dict['tranche'])
        if montant_avec_timbre > dict['max_value']:
           montant_avec_timbre = dict['max_value']
        if montant_avec_timbre < dict['min_value']:
           montant_avec_timbre = dict['min_value']

        res['timbre'] = montant_avec_timbre
        res['amount_timbre'] = montant + montant_avec_timbre

        return res




