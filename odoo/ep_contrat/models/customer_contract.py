from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
from werkzeug.urls import url_encode
from functools import partial
from odoo.tools.misc import formatLang, format_date


class CustomerContract(models.Model):
    _name = 'customer.contract'
    _description = 'Contrat Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    READONLY_STATES = {
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    AVAILABLE_PRIORITIES = [
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High'),
    ]

    name = fields.Char(string='Réference', states=READONLY_STATES, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Client', states=READONLY_STATES, tracking=True)
    # channel_id = fields.Many2one('mail.channel', default='')
    active = fields.Boolean(default=True)

    type_id = fields.Many2one('contract.type', string='Type', states=READONLY_STATES, tracking=True)
    type = fields.Selection([
        ('commercial', 'Commercial'),
        ('non-commercial', 'Non commercial'),
    ], string='Type', states=READONLY_STATES, tracking=True)
    start_date = fields.Date(string="Date début", states=READONLY_STATES, tracking=True)
    end_date = fields.Date(string="Date fin", states=READONLY_STATES, tracking=True)
    # duration = fields.Char(string="Durée", compute='_compute_duration', tracking=True, store=True )
    object = fields.Text(string="Objet du contrat",tracking=True, states=READONLY_STATES)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, required=True, tracking=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    contract_line_ids = fields.One2many('contract.line', 'customer_contract_id', string='Lignes de contrat', copy=True, tracking=True, states=READONLY_STATES)
    color = fields.Integer('Color Index', default=0)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)
    state = fields.Selection([
            ('draft', 'Brouillon'),
            ('progress', 'En cours'),
            ('done', 'Cloturé'),
            ('cancel', 'Annulé'),
        ], string='Etat', readonly=True, copy=False, index=True, tracking=True, default='draft', group_expand='_expand_states')

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    priority = fields.Selection(
        AVAILABLE_PRIORITIES, string='Priorité', index=True,
        default=AVAILABLE_PRIORITIES[0][0])

    # Relation with document
    doc_ids = fields.One2many("document", "customer_contract_id", string="Documents", tracking=True)

    # Relation with sale_order
    sale_order_ids = fields.One2many("sale.order", "customer_contract_id", string="Devis", tracking=True)
    sale_order_count = fields.Integer(string='Nombre de devis', compute='compute_sale_order', states=READONLY_STATES)

    # Amounts Fields
    amount_untaxed = fields.Monetary(string='Montant HT', currency_field='company_currency',store=True, readonly=True, compute='_amount_all', tracking=5)
    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group')
    amount_tax = fields.Monetary(string='Montant TVA', currency_field='company_currency', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', currency_field='company_currency', store=True, readonly=True, compute='_amount_all', tracking=4)

    # Reminder Fields
    customer_email = fields.Boolean("E-Mail au client", default=False)
    vendor_notification = fields.Boolean("Notification au vendeur", default=False)
    nbr_day_email = fields.Integer("Nombre de jours (e-mail)", help="Nombre de jours avant l'expiration du contrat pour envoyer l'email au client", default=0)
    nbr_day_notif = fields.Integer("Nombre de jours (notification)", help="Nombre de jours avant l'expiration du contrat pour envoyer la notification au vendeur", default=0)
    day_send_email = fields.Date("Jours d'envoie d'email", compute='_compute_send_email_day', store=True)
    day_display_notif = fields.Date("Jours d'envoie de notification", compute='_compute_display_notif_day',store=True)

    # To expand all state selection in kanban view
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange('customer_email', 'nbr_day_email', 'end_date')
    @api.depends('customer_email', 'nbr_day_email', 'end_date')
    def _compute_send_email_day(self):
        for rec in self:
            if rec.end_date and rec.customer_email:
                print("rec.end_date",rec.end_date)
                rec.day_send_email = rec.end_date - timedelta(days=rec.nbr_day_email)
                print("rec.day_send_email", rec.day_send_email)

    @api.onchange('vendor_notification', 'nbr_day_notif', 'end_date')
    @api.depends('vendor_notification', 'nbr_day_notif', 'end_date')
    def _compute_display_notif_day(self):
        for rec in self:
            if rec.end_date and rec.vendor_notification:
                print("rec.end_date",rec.end_date)
                print("rec.nbr_day_notif",rec.nbr_day_notif)
                rec.day_display_notif = rec.end_date - timedelta(days=rec.nbr_day_notif)
                print("rec.day_display_notif", rec.day_display_notif)

    @api.depends('contract_line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the customer contract
        """
        for record in self:
            amount_untaxed = amount_tax = 0.0
            for line in record.contract_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            record.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.contract_line_ids:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    @api.model
    def _default_note(self):
        return self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms or ''

    note = fields.Text('Terms and conditions', default=_default_note)

# @api.constrains('start_date', 'end_date')
    # def _compute_duration(self):
    #     for rec in self:
    #         if rec.start_date > rec.end_date:
    #             raise ValidationError('La date de début ne doit pas être inférieure à la date du fin')
    #         else:
    #         # if rec.end_date and rec.start_date:
    #             diff = (datetime.strptime(rec.end_date, '%Y-%m-%d')) - (datetime.strptime(rec.start_date, '%Y-%m-%d'))
    #             rec.duration = str(diff.days + 1)
    #             print((datetime.strptime(rec.end_date, '%Y-%m-%d')) - (datetime.strptime(rec.start_date, '%Y-%m-%d')))

    @api.model
    def create(self, vals):
        """
        Add specific sequence for each type of Contract
        :param vals:
        """
        seq = self.env['ir.sequence'].next_by_code('customer.contract.sequence') or '_(New)'
        # Affect sequence to Contract
        vals['name'] = seq
        return super(CustomerContract, self).create(vals)

    def unlink(self):
        """
        add constrains when delete a done contract_purchase
        """
        if self.filtered(lambda x: x.state in ('done')):
            raise UserError(_('Vous ne pouvez pas supprimer un contrat clôturé'))
        return super(CustomerContract, self).unlink()

    def button_start(self):
        self.write({'state': 'progress'})

    def button_done(self):
        self.write({'state': 'done'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    # @api.multi
    # def do_print(self):
    #     return self.env.ref('contrat.print_contract_master_report').report_action(self)

    def action_sale_order(self):
        self.ensure_one()
        context = dict(
            default_partner_id=self.partner_id.id,
            default_customer_contract_id=self.id,
            # default_order_line=self.contract_line_ids.ids,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Devis',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('customer_contract_id', '=', self.id)],
            'context': context
        }

    def compute_sale_order(self):
        for record in self:
            record.sale_order_count = self.env['sale.order'].search_count([('customer_contract_id', '=', record.id)])

    def preview_customer_contract(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def display_notification(self):
        notification_ids = []
        # notification_ids.append ((0,0,{
        #     'res_partner_id':self.partner_id.id,
        #     'notification_type':'inbox'}))
        # self.message_post(body='This receipt has been validated!', message_type='notification', subtype_id=self.env.ref('mail.mt_comment').id, author_id=self.env.user.partner_id.id, notification_ids=notification_ids)
        # self.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_comment',
        #                   notification_ids=notification_ids, email_layout_xmlid='mail.mail_notification_light')
        for rec in self:
            message = _("Reste %s jours pour l'expiration du contrat %s", rec.nbr_day_notif, rec.name)
            rec.message_post(body=message)
            # return self.message_post("Reste jours pour l'expiration du contrat ")
            domain = [('id', '=', 1)]
            channel = rec.env['mail.channel'].search(domain)
            if channel:
                channel.send_contract_notification(message)
                print("channel", channel)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'message': _("Reste %s jours pour l'expiration du contrat %s", rec.nbr_day_notif, rec.name),
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': True
                }
            }

    def execute_display_notification(self):
        for rec in self:
            if rec.vendor_notification and rec.day_display_notif == date.today():
               rec.display_notification()

    def send_email(self):
        # print("Send Email")
        template_id = self.env.ref('ep_contrat.email_expiration_ep_contrat').id
        template = self.env.ref('ep_contrat.email_expiration_contrat').browse(template_id)
        template.send_mail(self.id, force_send=True)

    def execute_send_email(self):
        for rec in self:
            if rec.customer_email and rec.day_send_email == date.today():
                rec.send_email()

    def send_email_with_wizard(self):
        '''
        This function opens a window to compose an email, with the email template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('ep_contrat', 'email_expiration_contrat')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'customer.contract',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }
        return {
            'name': _('Rédiger un email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def execute_send_email_cron(self):
        customer_contract = self.env['customer.contract'].search([])
        customer_contract.execute_send_email()

    def execute_display_notification_cron(self):
        customer_contract = self.env['customer.contract'].search([])
        print("notification")
        customer_contract.execute_display_notification()
