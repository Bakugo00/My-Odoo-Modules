# -*- coding: utf-8 -*-
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.addons.stock.models.stock_rule import ProcurementException


class StockRuleInherit(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(
            self,
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
    ):
        res = super()._prepare_mo_vals(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
            bom,
        )
        res["source_procurement_group_id"] = (
            values.get("group_id").id if values.get("group_id", False) else False
        )
        return res

    # Redefine this function to delete the confirmation of the generated manufacturing order
    # line 66
    @api.model
    def _run_manufacture(self, procurements):
        productions_values_by_company = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            bom = rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)
            if not bom:
                msg = _(
                    'There is no Bill of Material of type manufacture or kit found for the product %s. Please define a Bill of Material for this product.') % (
                      procurement.product_id.display_name,)
                errors.append((procurement, msg))

            productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))

        if errors:
            raise ProcurementException(errors)

        for company_id, productions_values in productions_values_by_company.items():
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(
                productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            productions._create_workorder()
            # productions.filtered(lambda p: not p.orderpoint_id and p.move_raw_ids).action_confirm()

            for production in productions:
                origin_production = production.move_dest_ids and production.move_dest_ids[
                    0].raw_material_production_id or False
                orderpoint = production.orderpoint_id
                if orderpoint:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': orderpoint},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
                if origin_production:
                    production.message_post_with_view('mail.message_origin_link',
                                                      values={'self': production, 'origin': origin_production},
                                                      subtype_id=self.env.ref('mail.mt_note').id)
        return True

