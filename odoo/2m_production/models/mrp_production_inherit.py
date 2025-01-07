import itertools

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MRPProductionInherit(models.Model):
    _inherit = "mrp.production"

    # @api.model
    # def _get_default_picking_type(self):
    #     company_id = self.env.context.get('default_company_id', self.env.company.id)
    #     return self.env['stock.picking.type'].search([
    #         ('code', '=', 'mrp_operation'),
    #         ('warehouse_id.company_id', '=', company_id),
    #     ], limit=1).id
    #
    # picking_type_id = fields.Many2one(
    #     'stock.picking.type', 'Operation Type', readonly=True,
    #     domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
    #     default=_get_default_picking_type, required=True, check_company=True)
    #
    # @api.model
    # def _get_default_location_dest_id(self):
    #     location = False
    #     company_id = self.env.context.get('default_company_id', self.env.company.id)
    #     if self._context.get('default_picking_type_id'):
    #         location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_dest_id
    #     if not location:
    #         location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
    #     return location and location.id or False
    #
    # location_dest_id = fields.Many2one(
    #     'stock.location', 'Finished Products Location',
    #     default=_get_default_location_dest_id,
    #     readonly=True, required=True,
    #     domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    #     # states={'draft': [('readonly', False)]}, check_company=True,
    #     help="Location where the system will stock the finished products.")

    # Redefine this fields to add readonly=True
    origin = fields.Char(
        'Source', copy=False, readonly=True,
        # states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'draft': [('readonly', True)]},
        help="Reference of the document that generated this production order request.")

    current_workorder_name = fields.Char('Etape de production', compute='_compute_current_workorder')

    @api.depends('workorder_ids')
    @api.onchange('workorder_ids')
    def _compute_current_workorder(self):
        for production in self:
            current_workorder_name = ''
            for workorder in production.workorder_ids:
                if workorder.state in ('progress', 'ready', 'done'):
                    current_workorder_name = workorder.operation_id.name
            production.current_workorder_name = current_workorder_name

    # Add this field in order to have the possibility to get sale order
    source_procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        readonly=True,
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Devis",
        readonly=True,
        store=True,
        related="source_procurement_group_id.sale_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="sale_id.partner_id",
        string="Client",
        store=True,
    )
    commitment_date = fields.Datetime(
        related="sale_id.commitment_date", string="Date de livraison", store=True
    )
    client_order_ref = fields.Char(
        related="sale_id.client_order_ref", string="Référence client", store=True
    )

    delivery_method = fields.Many2one('delivery.method',related="sale_id.delivery_method", string="Moyen de livraison", store=True)
    commercial_id = fields.Many2one(
        comodel_name="res.users",
        related="sale_id.user_id",
        string="Commerçial",
        store=True,
    )
    doc_ids = fields.One2many(related='sale_id.doc_ids', string="Documents", readonly=False)
    # product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value', compute='_compute_characteristics', string="Valeurs de caractéristiques")
    product_template_attribute_value_ids = fields.Many2many('option.value', compute='_compute_characteristics', string="Valeurs de caractéristiques")
    
    @api.depends('product_tmpl_id')
    def _compute_characteristics(self):
        product_template_attribute_value_ids = []
        line = self.sale_id.order_line.filtered(lambda line: line.product_template_id == self.product_tmpl_id and line.product_uom_qty == self.product_qty)[0]
        for crtsc in line.dynamic_option_ids:
            product_template_attribute_value_ids.append(crtsc.option_value_id.id)
        self.write({'product_template_attribute_value_ids':[(6, 0, product_template_attribute_value_ids)]})

    start_time = fields.Datetime(string='Start Time')
    remaining_time = fields.Float(string='Temps Restant', compute='_compute_remaining_time')

    @api.depends('start_time', 'date_planned_start')
    def _compute_remaining_time(self):
        for order in self:
            if order.start_time and order.date_planned_start:
                end_time = fields.Datetime.from_string(order.date_planned_start)
                current_time = fields.Datetime.now()
                remaining_time = (end_time - current_time).total_seconds()
                order.remaining_time = max(0, remaining_time)
            else:
                order.remaining_time = 0
    # choice_bat = fields.Selection([
    #     ('no_bat', 'Sans BAT'),
    #     ('bat', 'Avec BAT')], default='no_bat', string="Ajouter BAT")

    bat = fields.Boolean(string="Avec BAT")

    # Inherit this function and add constraint on workorder_ids.employee_ids and notifications to employees
    def action_confirm(self):
        res = super(MRPProductionInherit, self).action_confirm()
        # Comment this -> don't neet to affect employees
        # for workorder in self.workorder_ids:
        #     if not workorder.employee_ids:
        #         raise UserError(_("Vous devez préciser les employés de l'étape : %s") % workorder.name)

        for workorder in self.workorder_ids:
            notification_ids = []
            partner_ids = []

            msg = "Cet ordre de travail ( %s ) du l'ordre de production ( %s ) est assigné à vous " % (
                workorder.name, workorder.production_id.name)

            for employee in workorder.employee_ids:
                if employee.user_id:

                    notification_ids.append((0, 0, {
                        'res_partner_id': employee.user_id.partner_id.id,
                        'notification_type': 'inbox',
                    }))
                    partner_ids = [(4, employee.user_id.partner_id.id)]

            message = self.env['mail.message'].sudo().create(
                {
                    'message_type': 'notification',
                    'body': msg,
                    'subject': msg,
                    'model': 'mrp.workorder',
                    'res_id': workorder.id,
                    'partner_ids': partner_ids,
                    'author_id': self.env.user.partner_id.id,
                    'notification_ids': notification_ids,
                    'add_sign': True,
                    'record_name': False,
                }
            )

            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'type': 'warning',
            #         # 'type': 'success',
            #         'message': msg,
            #         'next': {'type': 'ir.actions.act_window_close'},
            #         'sticky': True
            #     }
            # }
        if self.workorder_ids:
            self.workorder_ids[0].button_start()
        self.start_time = fields.Datetime.now()
        return res

    component_id = fields.Many2one('product.template', string='Composant')
    component_qty = fields.Float('Quantité')
    parent_product = fields.Char('Produit Parent')
    def create(self,vals):
        #add this part to show new components
        res = super(MRPProductionInherit, self).create(vals)
        for mo in res:
            if mo.sale_id:
                lines = mo.sale_id.order_line.filtered(lambda line: line.product_template_id == mo.product_tmpl_id and line.product_uom_qty == mo.product_qty)
                if len(lines) > 1:
                    orders = res.filtered(lambda order: order.product_tmpl_id == mo.product_tmpl_id and order.product_qty == mo.product_qty )
                    for i in range(len(lines)):
                        orders[i].parent_product = lines[i].parent_product
                        #Reste de corriger les composant pour chaque ordre
                else:
                    mo.parent_product = lines[0].parent_product
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'sale_id' in groupby:
            self = self.with_context({'display_progression': True})
        return super(MRPProductionInherit, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
    
    # @api.model
    # def default_get(self, fields_list):
    #     res = super(MRPProductionInherit, self).default_get(fields_list)
    #     # print("---res", res)
    #     # workorder_ids = []
    #     # workorder = (0, 0, {
    #     #     'operation_id': self.env.ref('2m_production.conception').id,
    #     #     'production_id': self.id,
    #     #     # 'name': self.env.ref('2m_production.conception').name,
    #     #     # 'workcenter_id': self.env.ref('2m_production.conception').workcenter_id.id,
    #     # })
    #     # print("workorder_ids", workorder_ids)
    #     # workorder_ids.append(workorder)
    #     # print("workorder", workorder)
    #     # print("workorder_ids", workorder_ids)
    #     # res['product_qty'] = 120
    #     # res.update({
    #     #     # 'product_qty': 120,
    #     #     'workorder_ids': workorder_ids,
    #     # })
    #     operation_ids = self.env["mrp.routing.workcenter"].search([('sequence', 'in', (1,2,3,4))])
    #     print("res", res)
    #     workorders_values = []
    #     for operation in operation_ids:
    #         workorders_values += [
    #             {
    #                 'name': operation.name,
    #                 # 'production_id': res.id,
    #                 'workcenter_id': operation.workcenter_id.id,
    #                 # 'product_uom_id': self.env['uom.uom'].search([], limit=1, order='id').id,
    #                 'operation_id': operation.id,
    #                 # 'state': 'pending',
    #                 'consumption': 'flexible',
    #             }
    #         ]
    #
    #     workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
    #     res.update({
    #         'workorder_ids': workorder_ids,
    #     })
    #     print("res", res)
    #     return res

    # @api.onchange('bom_id')
    # def _onchange_workorder_ids(self):
    #     # if self.bom_id:
    #     #     self._create_workorder()
    #     # else:
    #
    #     operation_ids = self.env["mrp.routing.workcenter"].search([('sequence', 'in', (1,2,3,4))])
    #     workorders_values = []
    #     for operation in operation_ids:
    #         workorders_values += [
    #             {
    #                 'name': operation.name,
    #                 # 'production_id': self.id,
    #                 'workcenter_id': operation.workcenter_id.id,
    #                 'product_uom_id': self.product_uom_id.id,
    #                 'operation_id': operation.id,
    #                 'state': 'pending',
    #                 'consumption': self.consumption,
    #             }
    #         ]
    #
    #     workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
    #     # workorder_ids =  [(0, 0, value) for value in workorders_values]
    #
    #     self.workorder_ids = workorder_ids
    #     print(self.workorder_ids, ' workorder_ids')
    #     print(' workorder_ids')

