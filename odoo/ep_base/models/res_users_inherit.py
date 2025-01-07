
from odoo import api, fields, models, _, tools


class ResUsersInherit(models.Model):
    _inherit = "res.users"
    @api.model

    def _is_admin(self):
        context = self._context or {}
        if context.get('allow_group_by'):
            return True
        return super(ResUsersInherit, self)._is_admin()
    
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('access_group_user_id'):
            if context.get('access_group_user_id') == True:
                if self.env.user.has_group('ep_base.group_calendar_collaborateur'):
                    args = [('id','in',[self.env.user.id])]
                if self.env.user.has_group('ep_base.group_calendar_manager_n'):
                    args = ['|',('id','in',[self.env.user.id]),('employee_ids.parent_id', 'child_of', self.env.user.employee_ids.ids)]
                if self.env.user.has_group('ep_base.group_calendar_manager_it'):
                    args = [(1,'=',1)]

        return super(ResUsersInherit, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)
