from odoo import api, fields, models

class ProjectMilestoneType(models.Model):
    _name = 'project.milestone.type'
    _description = 'Type Project Milestone'
    name = fields.Char(string='Name', required=True)

class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'
    _description = 'Custom Project Milestone'
    start_date = fields.Date(store=True)
    type_milestone = fields.Many2one('project.milestone.type')
    deadline = fields.Date(required=True,tracking=True, copy=False)





