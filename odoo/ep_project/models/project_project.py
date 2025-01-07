from odoo import api, fields, models

class ProjectProject(models.Model):
    _inherit = "project.project"
    access_employees_ids = fields.Many2many('res.users', string='Employees with Access' )
    tasks_count = fields.Integer(string="Task count",compute='compute_count_tasks')

    def compute_count_tasks(self):
        for record in self:
            record.tasks_count = self.env['project.task'].search_count(
                [('project_id', '=', self.id)])

    def action_view_tasks(self):
        action = self.env['ir.actions.act_window']._for_xml_id('project.act_project_project_2_project_task_all')
        action["domain"] = [("project_id", "=",self.id)]
        return action
