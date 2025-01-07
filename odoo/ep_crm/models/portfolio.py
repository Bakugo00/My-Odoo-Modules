from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime as dt


class Portfolio(models.Model):
    _name = "portfolio"
    _description = "Portefeuille"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)

    active = fields.Boolean(default=True)

    categ_id = fields.Many2one('portfolio.category', string='Catégorie', tracking=True,  domain="[('company_ids', 'in', company_id)]")

    logged_user_id = fields.Many2one('res.users', string='Utilisateur Connecté', default=lambda self: self.env.user,
                                     readonly=True)

    owner_id = fields.Many2one('res.users', string='Propriétaire', default=lambda self: self.env.user, tracking=True,  domain="[('company_ids', 'in', company_id)]")

    user_ids = fields.Many2many('res.users', 'class_portfolio_users', 'portfolio_id', 'res_users_id',
                                string="Utilisateurs", tracking=True,  domain="[('company_ids', 'in', company_id)]")

    partner_ids = fields.Many2many('res.partner', 'class_portfolio_res_partner', 'portfolio_id', 'res_partner_id',
                                   string="Entreprises")

    partners_count = fields.Integer(string="Nombre d'entreprises", compute='compute_partners')

    goal = fields.Float(string='Objectif', store=True)

    turnover = fields.Float(string="Chiffre d'affaire réalisé", compute='compute_turnover')
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)


    # is_approved_user = fields.Integer(compute='compute_is_approved_user', store=True)
    #
    # portfolio_user_id = fields.Many2one('portfolio.user')
    #
    # portfolio_user_ids = fields.One2many('portfolio.user', string='Portefeuilles', inverse_name='portfolio_id')

    # is_approved_user = fields.Integer(compute='compute_is_approved_user_2', readonly=True, store=True, default=0)

    # @api.depends('logged_user_id','user_ids','owner_id')
    # def compute_is_approved_user_2(self):
    #     for record in self:
    #         approved = 0
    #         for port_user in record.portfolio_user_ids:
    #             if port_user.user_id == record.logged_user_id and port_user.portfolio_id == record.id:
    #                 approved = port_user.is_approved_user
    #
    #         record.is_approved_user = approved
    #         print("record.is_approved_user", record.is_approved_user)
    #         return approved

    # @api.model
    # def create(self, vals):
    #     portfolio = super(Portfolio, self).create(vals)
    #     if portfolio.owner_id:
    #         portfolio_user = self.env['portfolio.user'].create({
    #                      'user_id':  portfolio.owner_id.id,
    #                      'portfolio_id':  portfolio.id,
    #                      'is_approved_user':  1,
    #            })
    #         print("portfolio_user",portfolio_user)
    #     if portfolio.user_ids:
    #         for user in portfolio.user_ids:
    #             portfolio_user = self.env['portfolio.user'].create({
    #                 'user_id':  user.id,
    #                 'portfolio_id':  portfolio.id,
    #                 'is_approved_user':  1,
    #             })
    #
    #     return portfolio

    # @api.depends('logged_user_id', 'user_ids', 'owner_id')
    # def compute_is_approved_user(self):
    #     for record in self:
    #         approved = 0
    #         current_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
    #         if record.logged_user_id == record.owner_id:
    #             approved = 1
    #         if record.logged_user_id.id in record.user_ids.ids:
    #             approved = 1
    #
    #         record.is_approved_user = approved
    #         print("record.is_approved_user", record.is_approved_user)
    #         return approved

    @api.depends('partner_ids', 'name')
    def compute_partners(self):
        for record in self:
            count = 0
            count = len(record.env['res.partner'].search(
                [('id', 'in', record.partner_ids.ids)]))
            record.partners_count = count
            print(record.partners_count)

    # def _update_portfolio_cron(self):
    #     portfolio = self.env['portfolio'].search([])
    #     portfolio.compute_partners()
    #     portfolio.compute_turnover()

    @api.depends('partner_ids.turnover')
    def compute_turnover(self):
        for record in self:
            computed_turnover = 0
            for partner in record.partner_ids:
                computed_turnover += partner.turnover
            record.turnover = computed_turnover
            print("record.turnover",  record.turnover)

    def action_get_partners(self):
        self.ensure_one()
        context = dict(
            create=False,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partenaires',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'domain': [('portfolio_ids', 'in', self.id)],
            'context': context
        }

    def action_get_turnover(self):
        return True

    # TODO: Calculate The Goal
    def action_get_goal(self):
        return True

    def unlink(self):
        for recond in self:
            if recond.filtered(lambda x: x.partners_count != 0):
                raise ValidationError(_('Vous ne pouvez pas supprimer ce portefeuille ! il contient des entreprises'))
        return super(Portfolio, self).unlink()

    def move_companies(self):
        return self.env.ref('ep_crm.action_move_companies').read()[0]


# class PortfolioUserVisibility(models.Model):
#     _name = "portfolio.user"
#
#     is_approved_user = fields.Integer(compute='compute_is_approved_user', readonly=True, store=True)
#
#     user_id = fields.Many2one('res.users', string='User')
#
#     portfolio_id = fields.Many2one('portfolio', string='Portefieulle')

    # portfolio_ids = fields.One2many('portfolio', string='Portefieulles', inverse_name='portfolio_user_id')
