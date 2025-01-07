from odoo import api, fields, models, _


class SaleAttendeesAmount(models.Model):
    _name = "sale.attendees.amount"
    _rec_name = 'amount_participant'

    attendees_id = fields.Many2one(comodel_name='sale.attendees', ondelete='cascade')
    active = fields.Boolean(default=True)

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, required=True)

    user_id = fields.Many2one(comodel_name="res.users", string="Chargé de la vente", related="attendees_id.user_id", store=True)
    amount_participant = fields.Monetary(string="Montant HT", related="attendees_id.amount_participant", store=True)
    sale_order_id = fields.Many2one(comodel_name='sale.order', related="attendees_id.sale_order_id", store=True)
