# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, fields, models,_
from odoo.addons import project
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError
project.models.project.PROJECT_TASK_READABLE_FIELDS.add('legend_hold')
project.models.project.PROJECT_TASK_READABLE_FIELDS.add('legend_failed')
from datetime import timedelta  # Import timedelta from datetime module
from datetime import datetime
_logger = logging.getLogger(__name__)
import calendar

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    legend_hold = fields.Char(
        'Yellow Kanban Label', translate=True, required=True,
        help='Override the default value displayed for the hold state for kanban selection when the task or issue is in that stage.')
    legend_failed = fields.Char(
        'Red Kanban Label', translate=True, required=True)

class ProjectTask(models.Model):
    _inherit = "project.task"
    _order= "date_deadline asc, date_deadline_calculated asc"
    responsable = fields.Many2one('res.users', relation='project_task_user_rel', column1='task_id', column2='user_id', string='Responsable', context={'active_test': False}, tracking=True)
    description_technique = fields.Html(string='Description Téchnique')
    description_tests = fields.Html(string='Description Tests')
    code = fields.Char(string='Task Sequence', required=True, copy=False, readonly=True,
                                   default=lambda self: _('New'))
    kanban_state = fields.Selection(selection_add=[('hold', 'En pause'),('failed', 'Echouée')],
                                    ondelete={'hold': 'cascade','failed':'cascade'})
    

    legend_hold = fields.Char(related='stage_id.legend_hold', string='Kanban Valid Explanation', readonly=True,
                                related_sudo=False)
    legend_failed = fields.Char(related='stage_id.legend_failed', string='Kanban Valid Explanation', readonly=True,
    related_sudo=False)
    test_planned_hours = fields.Float("Test Planned Hours", tracking=True)
    milestone_id = fields.Many2one(
        'project.milestone',
        'Milestone',
        domain="[('project_id', '=', project_id)]",
        compute='_compute_milestone_id',
        readonly=False,
        store=True,
        required=True,
        tracking=True,
        index='btree_not_null',
        help="Deliver your services automatically when a milestone is reached by linking it to a sales order item."
    )
    date_deadline = fields.Date(string='Deadline', required=False, index=True, copy=False, tracking=True, task_dependency_tracking=True)
    date_deadline_calculated = fields.Date(string='Deadline Calculé', compute='_compute_deadline', store=True)
    description = fields.Html(string='Description', required=True, sanitize_attributes=False)
    user_story = fields.Boolean('User Story')
    show_icon = fields.Selection([('no_subtasks', 'No Sub-tasks'), ('has_subtasks', 'Has Sub-tasks')],string="Icon",
        compute='_compute_show_icon',
        store=True)
    subtask_count = fields.Integer(string='Nombre de sous-tâches', compute='_compute_subtask_count')
    planned_date = fields.Date(
        string='Date Prévisionnelle',
        compute='_compute_planned_date',
        store=True,
        readonly=True,
        help='Date prévisionnelle en fonction des délais actuels'
    )
    planned_hours = fields.Float(string="Heures allouées", required=True)
    date_start = fields.Date(string='Date de début', compute='_compute_date_start', store=True)
    date_end= fields.Date(string='Deadline', compute='_compute_date_end', store=True)
    predecessor_task_id = fields.Many2one('project.task', string='Tâche précédente',domain="[('project_id', '=', project_id)]")
    successor_task_id = fields.Many2one('project.task', string='Tâche suivante')

    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('project.task') or _('New')
        if 'predecessor_task_id' in vals:
            predecessor_task = self.browse(vals['predecessor_task_id'])
            if predecessor_task:
                date_start = predecessor_task.date_deadline + timedelta(days=1)
                while calendar.weekday(date_start.year, date_start.month, date_start.day) in (4, 5):
                    date_start += timedelta(days=1)
                vals['date_start'] = date_start
        return super(ProjectTask, self).create(vals)
    
    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            elif task.kanban_state == 'hold':
                task.kanban_state_label = task.legend_hold
            elif task.kanban_state == 'failed':
                task.kanban_state_label = task.legend_failed
            else:
                task.kanban_state_label = task.legend_done
    
    @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours','test_planned_hours')
    def _compute_progress_hours(self):
        
        for task in self:
            total_hours_planned = task.planned_hours+task.test_planned_hours
            if (total_hours_planned > 0.0):
                task_totall_hours = task.effective_hours + task.subtask_effective_hours
                task.overtime = max(task_totall_hours - total_hours_planned, 0)
                if float_compare(task_totall_hours, total_hours_planned, precision_digits=2) >= 0:
                    task.progress = 100
                else:
                    task.progress = round(100.0 * task_totall_hours / total_hours_planned, 2)
            else:
                task.progress = 0.0
                task.overtime = 0
    
    @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours','test_planned_hours')
    def _compute_remaining_hours(self):
        for task in self:
            total_hours_planned = task.planned_hours+task.test_planned_hours
            task.remaining_hours = total_hours_planned - task.effective_hours - task.subtask_effective_hours

    @api.onchange('date_deadline','milestone_id')
    def _onchange_date_deadline(self):
        if self.milestone_id.deadline and self.date_deadline and self.date_deadline > self.milestone_id.deadline:
                raise UserError("La date limite '%s' de la tâche ne peut pas être postérieure à la date limite '%s' du jalon associé."% (self.date_deadline,self.milestone_id.deadline))

    @api.depends('child_ids.date_deadline')
    def _compute_deadline(self):
        for task in self:
            # Filter out any False values before calculating max
            deadlines = [d for d in task.child_ids.mapped('date_deadline') if d]
            if deadlines:
                task.date_deadline_calculated = max(deadlines)
            else:
                task.date_deadline_calculated = False
    
    @api.depends('user_story', 'child_ids')
    def _compute_show_icon(self):
        for task in self:
            if task.user_story:
                if not task.child_ids:
                    task.show_icon = 'no_subtasks'
                else:
                    task.show_icon = 'has_subtasks'
            else:
                task.show_icon = False
    

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        for task in self:
            task.subtask_count = len(task.child_ids)
    
    @api.depends('date_deadline')
    def _compute_planned_date(self):
        for task in self:
            # Logique pour calculer la date prévisionnelle en fonction des retards
            # Exemple simplifié : ajouter 1 jour à la date limite actuelle
            if task.date_deadline:
                task.planned_date = task.date_deadline + timedelta(days=1)

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)

        # Check if the update involves changes to stage_id or child_ids
        if 'stage_id' in vals or 'child_ids' in vals:
            for task in self:
                # Ensure the task has child tasks
                if task.child_ids:
                    # Check if all child tasks are in the specified stages
                    if all(child.stage_id.name in ['FINISHED', 'DEPLOYED', 'REJECTED'] for child in task.child_ids):
                        # Find the new stage to set
                        new_stage = self.env['project.task.type'].search([('name', '=', 'FINISHED')], limit=1)
                        if new_stage:
                            # Update the parent task's stage_id with the ID of the 'FINISHED' stage
                            super(ProjectTask, task).write({'stage_id': new_stage.id})
        return res


    def write(self, vals):
        # Check if the update involves changes to date_deadline and if the context key is not set
        if 'date_deadline' in vals and not self.env.context.get('skip_deadline_extension'):
            # Convert the date_deadline to a datetime object for comparison
            new_deadline = fields.Date.from_string(vals['date_deadline'])
            for task in self:
                if task.date_deadline and new_deadline > fields.Date.from_string(task.date_deadline):
                    # Calculate the difference in days between the old and new deadline
                    delay = (new_deadline - fields.Date.from_string(task.date_deadline)).days

                    # Get related tasks based on the specified conditions
                    related_tasks = self.env['project.task'].search([
                        ('project_id', '=', task.project_id.id),
                        ('date_deadline', '>', task.date_deadline),
                        ('user_story', '=', False),
                        ('stage_id.name', 'not in', ['FINISHED', 'DEPLOYED', 'REJECTED'])
                    ])

                    # Extend the date_deadline of the related tasks
                    for related_task in related_tasks:
                        new_related_deadline = fields.Date.from_string(related_task.date_deadline) + timedelta(days=delay)
                        related_task.with_context(skip_deadline_extension=True).write({'date_deadline': new_related_deadline})
        
        # Perform the standard write operation
        return super(ProjectTask, self).write(vals)
        

    @api.depends('predecessor_task_id.date_deadline')
    def _compute_date_start(self):
        for task in self:
            if task.predecessor_task_id and task.predecessor_task_id.date_deadline:
                task.date_start = task.predecessor_task_id.date_deadline
            else:
                task.date_start = fields.Date.today()

    @api.depends('date_start', 'planned_hours')
    def _compute_date_end(self):
        for task in self:
            if task.date_start and task.planned_hours:
                working_days = task.planned_hours / 7.5
                deadline = task.date_start
                days_added = 0
                
                while days_added < working_days:
                    deadline += timedelta(days=1)
                    if calendar.weekday(deadline.year, deadline.month, deadline.day) not in (4, 5):  # Exclude Friday and Saturday
                        days_added += 1
                task.date_end = deadline        
                task.date_deadline = deadline