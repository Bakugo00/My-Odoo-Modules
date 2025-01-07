# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError, AccessError
from lxml import etree
import json

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    rc = fields.Char(string='Registre de commerce', tracking=True)
    nif = fields.Char(string='N° Id.Fiscal', size=20, tracking=True)
    nis = fields.Char(string='N° Id.Statistique', tracking=True)
    ai = fields.Char(string='Article d\'imposition', tracking=True)

    capital = fields.Float(string='Capital social', tracking=True)
    turnover = fields.Float(string="Chiffre d'affaire", tracking=True)
    nbr_employees = fields.Integer(string="Nombre d'employés", tracking=True)

    company_state_id = fields.Many2one('company.state', "Etat", tracking=True)
    company_status_id = fields.Many2one('company.status', "Status", tracking=True)
    company_type_id = fields.Many2one('company.type', "Type", tracking=True)
    email_ids = fields.One2many('email', 'partner_id', string='Emails', tracking=True)
    phone_ids = fields.One2many('phone', 'partner_id', string='Télephones', tracking=True)
    contact_type = fields.Selection([
        ('decider', 'Décideur'), ('collaborater', 'Collaborateur')
    ], string='Type')
    customer_state = fields.Selection(
        selection=[("suspect","Suspect"),("prospect", "Prospect"), ("client", "Client")],compute="_compute_customer_state", default="suspect")
    search_prospect_ids = fields.Char(compute="_compute_prospect_search_ids",search='search_prospects_ids_search')
    search_client_ids = fields.Char(compute="_compute_client_search_ids",search='search_client_ids_search')
    search_suspects_ids = fields.Char(compute="_compute_suspects_search_ids",search='search_suspects_ids_search')



    # customer_type = fields.Selection([
    #                          ('customer_true', "Client officiel"),
    #                          ('prospect', 'Prospect'),
    #                          ], string='Type de client', store=True, tracking=True, compute='_compute_customer_type')
    #
    # @api.depends('total_invoiced')
    # def _compute_customer_type(self):
    #     for partner in self:
    #         partner.customer_type = 'customer_true' if partner.total_invoiced > 0 else 'prospect'

    @api.constrains('name')
    def _check_partner_name(self):
        for record in self:
            count_name = record.search_count([('name', '=', record.name)])
            if count_name > 1 and record.name is not False:
                message = _('Le nom ( %s ) existe déja ! Vous devez chosir un autre nom') % \
                          (record.name)
                raise ValidationError(message)

    # Add store=True to company_type
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    compute='_compute_company_type', inverse='_write_company_type', store=True, tracking=True)


    # Add computed customer & supplier fields
    customer = fields.Boolean(compute='_compute_customer', inverse='_inverse_customer', store=True,
                              string="Est un client", tracking=True)
    supplier = fields.Boolean(compute='_compute_supplier', inverse='_inverse_supplier', store=True,
                              string="Est un fournisseur", tracking=True)

    @api.depends('customer_rank')
    def _compute_customer(self):
        for partner in self:
            partner.customer = True if partner.customer_rank > 0 else False

    def _inverse_customer(self):
        for partner in self:
            partner.customer_rank = 1 if partner.customer else 0

    def call_partner(self):
        # Define the URL you want to redirect to
        localhost = 'http://192.168.1.102/csbox/click-to-call.php?caller='
        if self.env.user.x_post_number:
            num_post=str(self.env.user.x_post_number) 
        else :
            raise ValidationError("Vous devez Configurer le numéro de Poste!")
        if self.mobile:
            contact_phone = '&called=' +str(self.mobile)
        else:
            raise ValidationError("Vous devez ajouter un numéro de téléphone pour ce contact!")
        url = localhost+num_post+contact_phone
        return {
            'type': 'ir.actions.act_url',
            'url':url ,
            'target': 'new',
        }

    @api.depends('supplier_rank')
    def _compute_supplier(self):
        for partner in self:
            partner.supplier = True if partner.supplier_rank > 0 else False

    def _inverse_supplier(self):
        for partner in self:
            partner.supplier_rank = 1 if partner.supplier else 0
    
    @api.depends('sale_order_count','invoice_ids','total_invoiced')
    def _compute_customer_state(self):
        for contact in self.sudo():
            invoices = contact.invoice_ids.filtered(lambda c : c.state not in ('draft','cancel') and c.move_type  in ('out_refund','out_invoice'))
            if contact.total_invoiced > 0:
                contact.customer_state = "client"
            elif contact.total_invoiced == 0 and invoices:
                contact.customer_state = "client"
            elif contact.sale_order_count !=0 :
                contact.customer_state = "prospect"
            else :
                contact.customer_state = "suspect"
    
    def _compute_prospect_search_ids(self):
        print('my compute')

    def search_prospects_ids_search(self,operator, operand):
        partner_ids_with_invoices = list(set(self.env['account.move'].search([('partner_id', '!=', False),('state','=','posted')]).mapped('partner_id').ids))
        partner_ids_with_sale_order = list(set(self.env['sale.order'].search([('partner_id', '!=', False)]).mapped('partner_id').ids))
        return [('id', 'not in', partner_ids_with_invoices),('id', 'in', partner_ids_with_sale_order),('company_type','=','company')]
            
    def _compute_client_search_ids(self):
        print('my compute')

    def search_client_ids_search(self,operator, operand):
        partner_ids_with_invoices = list(set(self.env['account.move'].search([('partner_id', '!=', False),('state','=','posted')]).mapped('partner_id').ids))
        return [('id', 'in', partner_ids_with_invoices),('company_type','=','company')]
            
    def _compute_suspects_search_ids(self):
        print('my compute')

    def search_suspects_ids_search(self,operator, operand):
        partner_ids_with_invoices = list(set(self.env['account.move'].search([('partner_id', '!=', False),('state','=','posted')]).mapped('partner_id').ids))
        partner_ids_with_sale_order = list(set(self.env['sale.order'].search([('partner_id', '!=', False)]).mapped('partner_id').ids))
        return [('id', 'not in', partner_ids_with_invoices),('id', 'not in', partner_ids_with_sale_order),('company_type','=','company')]
            


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('activity_partner_id') and context.get('activity_model') and context.get('activity_model')=='res.partner':
                args = [('company_type','=','person'),'|',('parent_id','in',[context.get('activity_partner_id')]),('id','=',context.get('activity_partner_id'))] 
        return super(ResPartnerInherit, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)