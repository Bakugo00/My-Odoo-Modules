from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from num2words import num2words


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    # ---------- Participation in invoice -------------------

    attendees_ids = fields.One2many(comodel_name="sale.attendees", inverse_name="account_move_id",
                                    string="Participants")

    total_participation = fields.Integer(string="Total Participation %", compute='_compute_total_participation',
                                         default=0, store=True)

    count_attendees = fields.Integer(string="Nombre de Participants", compute='_compute_nbr_attendees',
                                     default=0, store=True)

    @api.depends('attendees_ids')
    def _compute_nbr_attendees(self):
        for rec in self:
            count = 0
            if rec.attendees_ids:
                count = len(rec.attendees_ids)
            # print("count", count)
            rec.count_attendees = count

    @api.depends('attendees_ids', 'attendees_ids.participation')
    def _compute_total_participation(self):
        total_p = 0
        for rec in self:
            if rec.attendees_ids:
                for attendee in rec.attendees_ids:
                    total_p += attendee.participation
            rec.total_participation = total_p
        # print("sale_order.total_participation",sale_order.total_participation)

    @api.constrains('total_participation')
    def check_total_participation(self):
        for rec in self:
            if rec.attendees_ids and rec.filtered(lambda x: x.total_participation != 100):
                raise ValidationError(
                    _('Le total des pourcentages de participation est égale à %s ,Veuillez régler ces pourcentages !' % \
                      (rec.total_participation)))
