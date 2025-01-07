# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    contact_id = fields.Many2one('res.partner', string='Contact', tracking=True)

    amount_text = fields.Text(string="Montant en lettre", compute='_compute_amounts', store=True)

    negotiation_step_id = fields.Many2one('negotiation.step', string='Etapes de Négociation', tracking=True)

    customer_name = fields.Char(string="Nom", tracking=True)

    customer_address = fields.Char(string="Adresse", tracking=True)

    attendees_ids = fields.One2many(comodel_name="sale.attendees", inverse_name="sale_order_id", string="Participants")

    attendees_amount_ids = fields.One2many(comodel_name="sale.attendees.amount", inverse_name="sale_order_id",
                                           string="Montants Participants")

    total_participation = fields.Integer(string="Total Participation %", compute='_compute_total_participation',
                                         default=0, store=True)

    count_attendees = fields.Integer(string="Nombre de Participants", compute='_compute_nbr_attendees',
                                     default=0, store=True)

    customer_quotation_doc = fields.Binary(string="BC Client", tracking=True)

    file_name = fields.Char(string="Pièce jointe", tracking=True)

    state = fields.Selection(selection_add=[
        ('lost', 'Devis perdu'), ('sale',)
    ])

    devis_doublons = fields.Boolean(string='Devis doublons')
    
    devis_liste = fields.Many2one('sale.order', string='Chois de devis doublons')

    # stamp = fields.Selection([('non', 'Non'), ('oui', 'Oui')], string='Timbre', readonly=True, default='non',
    #                          states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    # amount_stamp = fields.Monetary(string="Montant Timbre", compute='_compute_amounts', store=True, default=0)


    # payment_method = fields.Selection([
    #     ('virement', 'Virement'),
    #     ('cheque', 'Chèque'),
    #     ('espece', 'Espèces')],
    #     string='Méthode de paiement', default='', required=True, tracking=True)

    def action_lost(self):
        for sale_order in self:
            sale_order.write({'state': 'lost'})

    # owner_id = fields.Many2one('res.users', string='Utilisateur Connecté', compute='_compute_user', default=lambda self: self.env.user, tracking=True, store=True)

    amount_participant_1 = fields.Monetary(string='Mon Montant', readonly=True, tracking=4, default=0)

    # compute='_compute_amount_participant_sale',
    # amount_participant = fields.Monetary(string='Montant Participant', store=True, readonly=True, tracking=4)

    # def _compute_user_ir_cron(self):
    #     sale_order = self.env['sale.order'].search([])
    #     sale_order._compute_user()
    #
    # def _compute_user(self):
    #     for record in self:
    #         # context = record._context
    #         # current_uid = context.get('uid')
    #         # record.owner_id = record.env['res.users'].browse(current_uid)
    #         record.owner_id = record.env.user
    #         # print("record.owner_id", record.owner_id)

    # def _compute_amount_participant_sale_order_ir_cron(self):
    #     rec = self.env['sale.order'].search([])
    #     rec._compute_amount_participant_sale_order()

    def _compute_amount_participant_sale_order(self):
        for record in self:
            print("IR CRON 1")
            for attendee in record.attendees_ids:

                print("IR CRON 2")
                print("attendee.user_id", attendee.user_id)
                print("self.env.user", self.env.user)
                if attendee.user_id == self.env.user:
                    print("IR CRON 3")
                    attendee.sale_order_id.amount_participant = attendee.amount_participant

                # amount = 0
                # domain = [
                #     ('user_id', '=', self.env.user.id),
                #     ('sale_order_id', '=', rec.sale_order_id.id),
                # ]
                # print("rec.env.user.id", rec.env.user.id)
                # print("self.env.user.id", self.env.user.id)
                # amount = sum(self.env['sale.attendees'].search(domain).mapped('amount_participant'))
                # # attendee = sale_order.env['sale.attendees'].search(domain)
                # # print("attendee", attendee)
                # # return attendee.amount_participant
                # # print("amount", amount)
                # # print("sale_order.logged_user_id", sale_order.logged_user_id)
                #
                # # domain = [
                # #     ('user_id', '=', sale_order.owner_id.id),
                # #     ('sale_order_id', '=', sale_order.id),
                # # ]
                # # amount = sale_order.env['sale.attendees.amount'].search(domain).mapped('amount_participant')
                # # # attendees_amount_ids
                # rec.sale_order_id.amount_participant = amount
                # print("IR CRON : rec.sale_order_id.amount_participant", rec.sale_order_id.amount_participant)

    @api.depends('attendees_ids')
    def _compute_nbr_attendees(self):
        for sale_order in self:
            count = 0
            if sale_order.attendees_ids:
                count = len(sale_order.attendees_ids)
            # print("count", count)
            sale_order.count_attendees = count

    @api.model
    def default_get(self, fields_list):
        # Put default salesman in participant list
        res = super(SaleOrderInherit, self).default_get(fields_list)
        # print("res", res)
        # attendees_ids = [(5,0,0)]
        attendees_ids = []
        attendee = (0, 0, {
            'user_id': res.get('user_id'),
            'participation': 100,
        })
        attendees_ids.append(attendee)
        res.update({
            'attendees_ids': attendees_ids,
        })
        return res
    
    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total')#,'payment_method'
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            super(SaleOrderInherit, order)._compute_amounts()
            # Add global discount calculation
            # amount_total = amount_untaxed = amount_tax =  amount_stamp = 0.0

            # for line in order.order_line:
            #     amount_untaxed += line.price_subtotal
            #     amount_tax += line.price_tax
            #     amount_total = amount_untaxed + amount_tax

            # if order.payment_method == 'espece':
            #     amount_stamp = int(amount_total * 0.01)
            # else:
            #     amount_stamp = 0

            # order.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            # order.amount_total = order.amount_untaxed + order.amount_tax
            # order.amount_stamp = amount_stamp
            order.amount_text = order.currency_id and order.currency_id.amount_to_text(order.amount_total ) or ''#+ amount_stamp


    # date_month = fields.Char(string='Date Month',compute='_get_date_month',store=True,readonly=True)
    # # @api.depends('date_order')
    # @api.onchange('date_order')
    # def _get_date_month(self):
    #     for order in self:
    #         order.date_month = dt.strptime(str(order.date_order),"%Y-%m-%d %H:%M:%S").strftime('%m')
    #         print(order.date_month)

    def _prepare_invoice(self):
        res = super(SaleOrderInherit, self)._prepare_invoice()

        # Create the attendees_ids for the account_move
        attendees_ids = []
        for attendee in self.attendees_ids:
            attendee = (0, 0, {
                'user_id': attendee.user_id,
                'participation': attendee.participation,
            })
            attendees_ids.append(attendee)

        res.update({
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'contact_id': self.contact_id.id,
            'attendees_ids': attendees_ids,
        })
        return res

    # @api.model
    # def create(self, vals):
    #     res = super(SaleOrderInherit, self).create(vals)
    #     # attendees_id = self.env['sale.attendees'].create(
    #     #     {
    #     #         'user_id': res.user_id.id,
    #     #         'participation': 100,
    #     #         'sale_order_id': res.id,
    #     #     })
    #     if res.attendees_ids:
    #         total_p = 0
    #         for attendee in res.attendees_ids:
    #             total_p += attendee.participation
    #
    #         if total_p != 100:
    #             raise ValidationError(
    #                 _('Le total des pourcentages de participation est égale à %s ,Veuillez régler ces pourcentages !' % \
    #                   (total_p)))
    #     return res

    @api.depends('attendees_ids', 'attendees_ids.participation')
    def _compute_total_participation(self):
        total_p = 0
        for sale_order in self:
            if sale_order.attendees_ids:
                for attendee in sale_order.attendees_ids:
                    total_p += attendee.participation
            sale_order.total_participation = total_p
        # print("sale_order.total_participation",sale_order.total_participation)

    @api.constrains('total_participation')
    def check_total_participation(self):
        for sale_order in self:
            if sale_order.attendees_ids and sale_order.filtered(lambda x: x.total_participation != 100):
                raise ValidationError(
                    _('Le total des pourcentages de participation est égale à %s ,Veuillez régler ces pourcentages !' % \
                      (sale_order.total_participation)))

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def default_customer_name_address(self):
        for sale_order in self:
            sale_order.customer_name = sale_order.partner_id.name
            sale_order.customer_address = sale_order.partner_id.street

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        # if not self.customer_quotation_doc:
        #     raise ValidationError(
        #         _('Veuillez joindre le bon de commande client cacheté et signé pour pouvoir confirmer la vente '))
        for line in self.order_line:
            # Confirm the product
            if line.product_template_id.confirmed_type == 'not-confirmed':
                line.product_template_id.confirmed_type = 'confirmed'
        return res
    
    def _copy_message_to_contact(self, body, **kwargs):
        # Check if there is a contact linked to the sale order
        if self.partner_id:
            if 'message_type' in kwargs:
                message_type = kwargs.get('message_type')
                if message_type == "comment":
            # Copy the message to the linked contact chatter
                    formatted_body = f"<b>{self.name} </b> <br> {body}"
                    self.partner_id.message_post(body=formatted_body, **kwargs)

    @api.model
    def message_post(self, body='', **kwargs):
        # Call the original message_post method
        result = super(SaleOrderInherit, self).message_post(body=body, **kwargs)
        
        # Copy the message to the linked contact chatter
        self._copy_message_to_contact(body, **kwargs)

        return result





