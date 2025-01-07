from odoo import api, fields, models, _


class SaleAttendees(models.Model):
    _name = "sale.attendees"
    _description = "Participants du devis"
    _rec_name = 'amount_participant'

    user_id = fields.Many2one(comodel_name="res.users", string="Chargé de la vente")
    participation = fields.Integer(string="Participation %", default=0)
    sale_order_id = fields.Many2one(comodel_name='sale.order')
    account_move_id = fields.Many2one(comodel_name='account.move')
    # sale_order_line_id = fields.Many2one(comodel_name='sale.order.line')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, required=True)
    # currency_id = fields.Many2one(related='sale_order_id.currency_id', depends=['sale_order_id.currency_id'], store=True, string='Currency', readonly=True)
    amount_untaxed_sale = fields.Monetary(string="Montant HT", related="sale_order_id.amount_untaxed")
    amount_untaxed_invoice = fields.Monetary(string="Montant HT", related="account_move_id.amount_untaxed")
    amount_participant = fields.Monetary(string='Montant', store=True, readonly=True,
                                         compute='_compute_amount_participant', tracking=5)

    state = fields.Selection(related='sale_order_id.state', store=True)
    date_order = fields.Datetime(related='sale_order_id.date_order', store=True)
    active = fields.Boolean(default=True)

    def unlink(self):
        for record in self:
            # Put the participation and amount_participant to 0 when unlinking the record
            record.participation = 0
            record.amount_participant = 0
        return super(SaleAttendees, self).unlink()

    @api.depends('amount_untaxed_sale', 'amount_untaxed_invoice', 'participation')
    def _compute_amount_participant(self):
        for record in self:
            amount_participant = 0
            if record.sale_order_id:
                amount_participant = (record.amount_untaxed_sale * record.participation) / 100
            if record.account_move_id:
                amount_participant = (record.amount_untaxed_invoice * record.participation) / 100
            record.amount_participant = amount_participant

    @api.model
    def create(self, vals):
        res = super(SaleAttendees, self).create(vals)
        attendees_amount_id = self.env['sale.attendees.amount'].sudo().create(
            {
                'attendees_id': res.id,
                # 'sale_order_id': res.sale_order_id.id,
            })
        # print("attendees_amount_id",attendees_amount_id)

        return res
