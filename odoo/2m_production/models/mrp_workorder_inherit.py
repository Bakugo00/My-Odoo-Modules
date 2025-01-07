from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    # _inherit = ['mrp.workorder', 'mail.thread', 'mail.activity.mixin']

    sale_id = fields.Many2one(
        related="production_id.sale_id", string="Devis", readonly=True, store=True
    )
    partner_id = fields.Many2one(
        related="sale_id.partner_id", readonly=True, string="Client", store=True
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date",
        string="Date de livraison",
        store=True,
        readonly=True,
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Référence client", store=True
    )

    # Redefine this field to change required=True to required=False
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order', required=False, check_company=True,
                                    readonly=True)
    employee_ids = fields.Many2many('hr.employee', string="Employés")

    # Relation with document
    doc_ids = fields.One2many("document", "mrp_workorder_id", string="Documents", tracking=True)

    name = fields.Char(
        'Description', required=True, invisibe=True)

    state = fields.Selection(selection_add=[
        ('validate', 'Validé'),
    ])
    imprimante = fields.Char('Imprimante')

    def button_validate(self):
        for workorder in self:
            workorder.write({'state': 'validate'})
            message = _("Valider l'ordre de travail ( %s ) par ( %s )", workorder.name, self.env.user.partner_id.name)
            workorder.production_id.message_post(body=message, author_id=self.env.user.partner_id.id)

            workorder._start_nextworkorder()

    # Do the same thing as button_start
    def button_restart(self):
        self.ensure_one()

        if self.product_tracking == 'serial':
            self.qty_producing = 1.0
        else:
            self.qty_producing = self.qty_remaining

        self.env['mrp.workcenter.productivity'].create(
            self._prepare_timeline_vals(self.duration, datetime.now())
        )
        if self.production_id.state != 'progress':
            self.production_id.write({
                'date_start': datetime.now(),
            })
        if self.state == 'progress':
            return True
        start_date = datetime.now()
        vals = {
            'state': 'progress',
            'date_start': start_date,
        }
        if not self.leave_id:
            leave = self.env['resource.calendar.leaves'].create({
                'name': self.display_name,
                'calendar_id': self.workcenter_id.resource_calendar_id.id,
                'date_from': start_date,
                'date_to': start_date + relativedelta(minutes=self.duration_expected),
                'resource_id': self.workcenter_id.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            # return self.write(vals)
        else:
            if self.date_planned_start > start_date:
                vals['date_planned_start'] = start_date
            if self.date_planned_finished and self.date_planned_finished < start_date:
                vals['date_planned_finished'] = start_date
            # return self.write(vals)
        # Post the message of restarting
        message = _("Relancer l'ordre de travail ( %s ) par ( %s )", self.name, self.env.user.partner_id.name)
        self.production_id.message_post(body=message, author_id=self.env.user.partner_id.id)
        message2 = _("L'étape <b>%s</b> à été relancée par  <b>%s</b>.(Article <b>%s</b>)", self.name, self.env.user.partner_id.name ,self.production_id.product_id.name)
        self.production_id.sale_id.message_post(body=message2, author_id=self.env.user.partner_id.id)
        return self.write(vals)

    # Redefine this function to delete the start of the next workorder
    def button_finish(self):
        end_date = datetime.now()
        for workorder in self:
            if workorder.state in ('done', 'cancel'):
                continue
            workorder.end_all()
            vals = {
                'qty_produced': workorder.qty_produced or workorder.qty_producing or workorder.qty_production,
                'state': 'done',
                'date_finished': end_date,
                'date_planned_finished': end_date
            }
            if not workorder.date_start:
                vals['date_start'] = end_date
            if not workorder.date_planned_start or end_date < workorder.date_planned_start:
                vals['date_planned_start'] = end_date
            workorder.write(vals)
            # Post the message of finish
            message = _("Terminer l'ordre de travail ( %s ) par ( %s )", workorder.name, self.env.user.partner_id.name)
            workorder.production_id.message_post(body=message, author_id=self.env.user.partner_id.id)
            message2 = _("L'étape <b>%s</b> à été terminée.(Article <b>%s</b>)", workorder.name ,workorder.production_id.product_id.name)
            workorder.production_id.sale_id.message_post(body=message2, author_id=self.env.user.partner_id.id)

            # workorder._start_nextworkorder()
        return True

    # Inherit this function and add the post of a message
    def button_start(self):
        res = super(MrpWorkorder, self).button_start()
        for workorder in self:
            # Post the message of finish
            message = _("Démarrer l'ordre de travail ( %s ) par ( %s )", workorder.name, self.env.user.partner_id.name)
            workorder.production_id.message_post(body=message, author_id=self.env.user.partner_id.id)
            message2 = _("La production est dans l'étape: <b>%s</b>, Utilisateur: <b>%s</b> .(Article <b>%s</b>)", workorder.name, self.env.user.partner_id.name,workorder.production_id.product_id.name)
            workorder.production_id.sale_id.message_post(body=message2, author_id=self.env.user.partner_id.id)
        return res

    # Inherit this function and add the post of a message
    def button_pending(self):
        res = super(MrpWorkorder, self).button_pending()
        for workorder in self:
            # Post the message of finish
            message = _("Mettre en pause l'ordre de travail ( %s ) par ( %s )", workorder.name,
                        self.env.user.partner_id.name)
            workorder.production_id.message_post(body=message, author_id=self.env.user.partner_id.id)
        return res

    # Redefine this function to change self.state == 'done' to self.state == 'validate'
    def _start_nextworkorder(self):
        if self.state == 'validate' and self.next_work_order_id.state == 'pending':
            self.next_work_order_id.state = 'ready'
            self.next_work_order_id.button_start()

    def send_email(self):
        '''
        This function opens a window to compose an email, with the email template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('2m_production', 'email_to_customer_in_workorder')[1]
        except ValueError:
            template_id = False

        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = {
            'default_model': 'mrp.workorder',
            'active_model': 'mrp.workorder',
            'active_id': self.ids[0],

            # 'default_model': 'mrp.workorder',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'name': _('Rédiger un email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
