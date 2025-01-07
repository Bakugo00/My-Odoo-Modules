from odoo import models, api, exceptions,fields

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    @api.model
    def getEmployeeDomain(self):
        return [('parent_id', 'child_of', self.env.user.employee_id.id)]
    
    note = fields.Text(string='Note')
    employee_id = fields.Many2one('hr.employee',domain = lambda self: self.getEmployeeDomain())

    def write(self, vals):
        for rec in self:
            if ((rec.check_in and 'check_in' in vals) or (rec.check_out and 'check_out' in vals)):
                if not vals.get('note') and not rec.note:
                    raise exceptions.ValidationError("Une note est requise lors de la modification d'un pointage.")
        return super(HrAttendance, self).write(vals)