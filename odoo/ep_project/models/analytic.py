from odoo import api, fields, models,_


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.line'
    _description = 'Custom Analytic Line'
    
    type = fields.Selection(
        [('other', 'Other'),
        ('management', 'Management'),
        ('specification', 'Specification'),
        ('developement','Developement'),
        ('testing','Testing'),
        ('support','Support')],
        default='other',
    )
    successful_test = fields.Boolean(string="Test Concluant", default=False, copy=False)
    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        domain = domain or []
        if self.env.context.get('my_team_timesheets') == True:
            domain.extend(['|', ('employee_id.user_id', '=', self.env.user.id), ('employee_id.parent_id', 'in', self.env.user.employee_ids.ids),('employee_id','!=',False)])
        return super(AccountAnalyticAccount, self).search_read(domain, fields, offset, limit, order)