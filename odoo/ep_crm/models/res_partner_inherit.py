# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    portfolio_ids = fields.Many2many('portfolio', 'class_portfolio_res_partner', 'res_partner_id' , 'portfolio_id', string="Portefeuilles", readonly=False, store=True,required=False)
    viewer_ids = fields.Many2many('res.users')
    show_form = fields.Boolean(compute="compute_show_form",default=False)
    # viewer_ids = fields.Many2many('res.users')

    @api.onchange('portfolio_ids')
    def _onchange_portfolio_ids(self):
        if self.portfolio_ids:
            # Get the names of all partners in the portfolio's partner_ids
            portfolio_partner_names = self.portfolio_ids.mapped('partner_ids.name')

            # Apply the domain to filter partners whose names are not in the portfolio_partner_names
            return {
                'domain': {
                    'partner_id': [('name', 'not in', portfolio_partner_names)]
                }
            }
        else:
            return {
                'domain': {
                    'partner_id': []
                }
            }

    @api.onchange('portfolio_ids')
    @api.depends('portfolio_ids')
    def compute_viewers(self):
        for record in self:
            for portfolio in record.portfolio_ids:

                    record.viewer_ids = record.viewer_ids + portfolio.user_ids + portfolio.owner_id
                    # record.viewer_ids = [(6, 0, portfolio.user_ids.ids )]
                    # print("record.viewer_ids ",  record.viewer_ids)
    @api.model
    def _commercial_fields(self):
        commercial_fields = super(ResPartnerInherit, self)._commercial_fields()
        new_commercial_fields = ['portfolio_ids']
        commercial_fields.extend(new_commercial_fields)
        return commercial_fields
    
    def get_partners_in_portoflios(self):
        current_user = self.env.user
        partners = self.env['res.partner'].browse([])
        if current_user.has_group('ep_crm.group_contacts_collaborateur'):
            partners |= self.env['res.partner'].search(['|', ('portfolio_ids.owner_id.id', 'in', [current_user.id]), ('portfolio_ids.user_ids.id', 'in', [current_user.id])])

        if current_user.has_group('ep_crm.group_contacts_manager_n'):
            partners |= self.env['res.partner'].search(['|', ('portfolio_ids.owner_id.employee_ids.parent_id', 'child_of', current_user.employee_ids.ids), ('portfolio_ids.user_ids.employee_ids.parent_id', 'child_of', current_user.employee_ids.ids)])

        if current_user.has_group('ep_crm.group_contacts_manager') or current_user.has_group('ep_crm.group_contacts_manager_rh'):
            partners |= self.env['res.partner'].search([])
        return partners
    
    @api.depends('portfolio_ids','portfolio_ids.owner_id', 'portfolio_ids.user_ids')
    def compute_show_form(self):
        partners = self.get_partners_in_portoflios()
        for partner in self: partner.show_form = True
        partners_ = self - partners 
        for partner in partners_ : partner.show_form = False
     
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('show_portoflio_contacts'):
            if context.get('show_portoflio_contacts') == True:
                if self.env.user.has_group('ep_crm.group_contacts_collaborateur'):
                    args.append('|')
                    args.extend([
                    ('portfolio_ids.owner_id.id','in',[self.env.user.id]),
                    ('portfolio_ids.user_ids.id','in',[self.env.user.id])])
                    #if args is empty the result of args = ['|',('portfolio_ids.owner_id.id','in',[self.env.user.id]),('portfolio_ids.user_ids.id','in',[self.env.user.id])]
                if self.env.user.has_group('ep_crm.group_contacts_manager_n'):
                    args.append('|')
                    args.append('|')
                    args.extend([
                    ('portfolio_ids.owner_id.id','in',[self.env.user.id]),
                    ('portfolio_ids.user_ids.id','in',[self.env.user.id]),'|',
                    ('portfolio_ids.owner_id.employee_ids.parent_id', 'child_of', self.env.user.employee_ids.ids),
                    ('portfolio_ids.user_ids.employee_ids.parent_id', 'child_of', self.env.user.employee_ids.ids)])
                    #if args is empty the result of args = ['|','|',('portfolio_ids.owner_id.id','in',[self.env.user.id]),('portfolio_ids.user_ids.id','in',[self.env.user.id]),'|', ('portfolio_ids.owner_id.employee_ids.parent_id', 'child_of', [self.env.user.employee_ids.id]), ('portfolio_ids.user_ids.employee_ids.parent_id', 'child_of', [self.env.user.employee_ids.id])]
                if self.env.user.has_group('ep_crm.group_contacts_manager') or self.env.user.has_group('ep_crm.group_contacts_manager_rh'):
                    args.extend([(1,'=',1)])
                    #if args is empty the result of args = [(1,'=',1)]

        return super(ResPartnerInherit, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
