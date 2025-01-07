# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools, Command
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import timedelta, datetime as dt
from collections import defaultdict
from odoo.tools.misc import clean_context
from lxml import etree


class MailActivityInherit(models.Model):
    _name = "mail.activity"
    _inherit = ["mail.activity","mail.thread"]
    _order = "date_deadline desc"

    result_categ_id = fields.Many2one(string="Catégorie de résultat", comodel_name="activity.result.category", tracking=True)

    result_id = fields.Many2one(string="Résultat", comodel_name="activity.result", tracking=True)
    contact_id = fields.Many2one('res.partner', string='Contact', tracking=True,
        domain="[('company_id', 'in', (False, company_id)),('company_type','=','person')]")
    company_id = fields.Many2one(
        comodel_name='res.company', required=True,
        default=lambda self: self.env.company)
    sources = fields.Selection([
        ('other', 'Autres'),('search_eng', 'moteurs de recherche (google yahoo bing ...)'),('social_media', 'Réseaux sociaux'),
        ('link', 'Lien sur un autre site'),('press', 'par la presse '),('wom', 'Bouche à oreille ')
    ], string='Autre Source', tracking=True)
    time_deadline = fields.Float("heure d'écheance", tracking=True)
    date_deadline = fields.Date(string="Date de l'évenement", tracking=True)
    state = fields.Selection(tracking=True)
    res_name = fields.Char( tracking=True)
    summary = fields.Char( tracking=True)
    activity_type_id = fields.Many2one('mail.activity.type', tracking=True, default=False)
    user_id = fields.Many2one('res.users', tracking=True, readonly=True, default=lambda self: self.env.uid)
    has_activity = fields.Boolean(compute='_update_has_activity' ,default=False,store=True)
    participants = fields.Many2many('res.users', string='Participants')
    reminder_type_id = fields.Many2one('mail.activity.type', string="Type de rappel" ,tracking=True, default=False)
    reminder_date = fields.Date(string='Date de rappel', required=True, default=dt.today())
    reminder_time = fields.Float(string='Temps de rappel', required=True)
    reminder_note = fields.Text(string='Note')
    reminder_summary = fields.Char( tracking=True, string="Résumé de rappel")
    is_reminder = fields.Boolean(string='Is Reminder', default=False)
    related_activity = fields.Many2one('mail.activity', tracking=True, string="Activité en relation")
    is_event_closed = fields.Boolean(string='Event Closed', default=False)

    @api.onchange('is_event_closed')
    def _onchange_is_event_closed(self):
        if self.is_event_closed:
            self.action_done()

    @api.model
    def get_related_activity_types_domain(self):
        activity_types_set = set()
        category_ids = self.env['activity.result.category'].search([])  # Retrieve all activity.result.category records
        for category in category_ids:
            for activity_type in category.type_ids:
                activity_types_set.add(activity_type.id)
        return [("id", "in", list(activity_types_set))]

    @api.depends('contact_id','user_id')
    def _update_has_activity(self):
        for record in self:
            if record.contact_id:
                existing_activities = self.env['mail.activity'].search([
                ('contact_id', '=', record.contact_id.id),
                ('user_id', '=', record.user_id.id)
            ])
                if existing_activities:
                    record.has_activity = True
                else:
                    record.has_activity = False
                  
    
    @api.model
    def create(self, vals):
        user_id = vals.get('user_id') or self.env.uid # Get user ID from vals or use current user
        contact_id = vals.get('contact_id')
        is_reminder = vals.get('is_reminder')
        
        # Ensure we are working with a regular activity, not a reminder
        if contact_id and user_id and not is_reminder:
            # Search for any activities created by the same user for the same contact within the last 10 minutes
            recent_activity = self.env['mail.activity'].search([
                    ('user_id', '=', user_id),
                    ('contact_id', '=', contact_id),
                    ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=10)),
                ])
            # If a recent activity exists, raise a ValidationError
            if recent_activity:
                raise UserError("You cannot create an activity within 10 min")
        res = super(MailActivityInherit, self).create(vals)
        return res
        
    # Redefine this function to verify if categ result and result are filled before ending an activity
    def action_done_schedule_next(self):
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """

        # Verification
        for activity in self:
            info = ""
            if not activity.result_categ_id:
                info += "\n" + " - La catégorie de résultat " + "\n"
            if not activity.result_id:
                info += " - Le résultat" + "\n"
            if not activity.contact_id:
                info += " - Le contact" + "\n"
            message = _("Avant de clôturer l'activité , veuillez préciser : %s") % \
                      info

            if not (activity.result_categ_id and activity.result_id and activity.contact_id):
                raise ValidationError(message)

        return self.action_feedback_schedule_next()

    # Redefine this function to pass fields from mail_activity to mail_message
    # and verify if categ result and result are filled before ending an activity
    def _action_done(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for model, activity_data in self._classify_by_model().items():
            records = self.env[model].browse(activity_data['record_ids'])
            for record, activity in zip(records, activity_data['activities']):
                # Verify if categ result and result are filled
                info = ""
                if not activity.result_categ_id:
                    info += "\n" + " - La catégorie de résultat " + "\n"
                if not activity.result_id:
                    info += " - Le résultat" + "\n"
                if not activity.contact_id:
                    info += " - Le contact" + "\n"
                message = _("Avant de clôturer l'activité , veuillez préciser : %s") % \
                        info

                if not (activity.result_categ_id and activity.result_id and activity.contact_id):
                    raise ValidationError(message)
                # extract value to generate next activities
                if activity.chaining_type == 'trigger':
                    vals = activity.with_context(activity_previous_deadline=activity.date_deadline)._prepare_next_activity_values()
                    next_activities_values.append(vals)

                # post message on activity, before deleting it
                activity_message = record.message_post_with_view(
                    'mail.message_activity_done',
                    values={
                        'activity': activity,
                        'feedback': feedback,
                        'display_assignee': activity.user_id != self.env.user
                    },
                    subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_activities'),
                    mail_activity_type_id=activity.activity_type_id.id,
                    attachment_ids=[Command.link(attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
                )

                # Moving the attachments in the message
                # TODO: Fix void res_id on attachment when you create an activity with an image
                # directly, see route /web_editor/attachment/add
                if activity_attachments[activity.id]:
                    message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
                    if message_attachments:
                        message_attachments.write({
                            'res_id': activity_message.id,
                            'res_model': activity_message._name,
                        })
                        activity_message.attachment_ids = message_attachments
                messages += activity_message
                # Update the messages extras values
                messages.result_categ_id = activity.result_categ_id
                messages.result_id = activity.result_id
                messages.contact_id = activity.contact_id
                messages.date_deadline = activity.date_deadline
                messages.summary = activity.summary
                messages.user_id = activity.user_id
                messages.company_id = activity.company_id

        next_activities = self.env['mail.activity']
        if next_activities_values:
            next_activities = self.env['mail.activity'].create(next_activities_values)

        self.unlink()  # will unlink activity, dont access `self` after that

        return messages, next_activities
    
    
    # The change i made is designed to manage scenarios where an activity is marked as completed within the same form view, 
    # It aims to prevent validation errors and ensure smooth operation of the system.
    def action_feedback_schedule_next(self, feedback=False, attachment_ids=None):
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            activity_previous_deadline=self.date_deadline,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
        )
        _messages, next_activities = self._action_done(feedback=feedback, attachment_ids=attachment_ids)  # will unlink activity, dont access self after that
        if next_activities and self._context.get('target_current'):
            tree_view_id = self.env.ref('mail.mail_activity_view_tree').id
            form_view_id = self.env.ref('mail.mail_activity_view_form').id
            return {
                'name': _('Activity'),
                'view_mode': 'tree',
                'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                'res_model': 'mail.activity',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        if next_activities:
            return False
        if self._context.get('target_current'):
            # Modify the result to set the target to 'current' if 'current' key is present
            view_id = self.env.ref('mail.mail_activity_view_form').id
            return {
                'name': _('Schedule an Activity'),
                'context': ctx,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.activity',
                'views': [(view_id, 'form')],
                'view_id': view_id,
                'target': 'current'
            }
        else : 
            return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    
    # Same for this function. The change I made is designed to manage scenarios where an activity is marked as completed within the same form view.
    # It aims to prevent validation errors and ensure smooth operation of the system.
    def action_feedback(self, feedback=False, attachment_ids=None):
        messages, _next_activities = self.with_context(
            clean_context(self.env.context)
        )._action_done(feedback=feedback, attachment_ids=attachment_ids)
        if self._context.get('target_current'):
            tree_view_id = self.env.ref('mail.mail_activity_view_tree').id
            form_view_id = self.env.ref('mail.mail_activity_view_form').id
            return {
                'name': _('Activity'),
                'view_mode': 'tree',
                'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                'res_model': 'mail.activity',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        else:
            return messages[0].id if messages else False
    
    def action_create_calendar_event(self):
        action = super(MailActivityInherit, self).action_create_calendar_event()
        context={'default_partner_ids' : [(6, 0, self.participants.mapped('partner_id').ids)]}
        action['context'].update(context)

        return action
    
    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        rec_list = ['user_id']
        for field in arch.xpath("//field"):
            if field.get('name') in rec_list:
                field.set('readonly', '1') if not self.env.user.has_group('ep_vente.group_sale_order_n') else field.set('readonly', '0')
        return arch, view

    def action_close_dialog(self):
    # Iterate over each record in self
        for record in self:
            # Check if the current record has the necessary reminder fields
            if record.contact_id and record.reminder_date:
                # Prepare the values for the reminder (rappel)
                reminder_vals = {
                    'activity_type_id': record.reminder_type_id.id,  # or a different type if needed
                    'date_deadline': record.reminder_date,
                    'time_deadline': record.reminder_time,
                    'summary': record.reminder_summary,
                    'contact_id': record.contact_id.id,
                    'note': record.reminder_note,
                    'user_id' : record.user_id.id,
                    'related_activity' : record.id,
                    'is_reminder': True,  # Optional flag to distinguish reminders
                    # Include other necessary fields here
                }

                # Create the reminder record using the appropriate model
                reminder = self.env['mail.activity'].create(reminder_vals)
        # Close the dialog or show confirmation
        return {'type': 'ir.actions.act_window_close'}
    
    def action_done(self):
        for activity in self:
            if activity.related_activity:  # Assuming `related_activity` is the field pointing to the parent
                raise UserError(_("You need to mark the parent activity as done first"))
            
            # Mark the current activity as done
            return super(MailActivityInherit, self).action_done()







