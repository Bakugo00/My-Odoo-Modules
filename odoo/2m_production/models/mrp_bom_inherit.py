import itertools

from odoo import api, fields, models, _


class MRPBomInherit(models.Model):
    _inherit = "mrp.bom"

    # change opearations_ids from One2many to Many2many
    operation_ids = fields.Many2many('mrp.routing.workcenter')

    # Override
    @api.model
    def default_get(self, fields_list):
        res = super(MRPBomInherit, self).default_get(fields_list)
        operation_ids = self.env["mrp.routing.workcenter"].search([('sequence', 'in', (1,2,3,4))])
        # operations_values = []
        # print("get_operation_ids", operation_ids)
        #
        # for operation in operation_ids:
        #     operations_values += [
        #         {
        #             'name': operation.name,
        #             # 'bom_id': res.id,
        #             'workcenter_id': operation.workcenter_id.id,
        #             # 'product_uom_id': res.product_uom_id.id,
        #             # 'operation_id': operation.id,
        #             # 'state': 'pending',
        #             # 'consumption': res.consumption,
        #         }
        #     ]
        #
        # operation_ids = [(5, 0)] + [(0, 0, value) for value in operations_values]
        # print("operation_ids", operation_ids)
        res.update({
            'operation_ids': operation_ids,
        })
        return res