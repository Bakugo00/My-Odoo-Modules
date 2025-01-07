# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from datetime import datetime as dt


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Remise (%)', digits=(16, 20), default=0.0)

    # def _get_default_vendor(self):
    #     for line in self:
    #         return line.env["res.users"].search([('id', '=', line.order_id.user_id)])
    #         # return line.order_id.user_id
    #
    # def _get_default_participation(self):
    #     # for line in self:
    #         so = self.env['sale.order'].browse(self._context.get('active_ids', []))
    #         print("so", so)
    #         per = 100
    #         sale_order = self.env["sale.order"].search([('id', '=', self.order_id.id)])
    #         print("sale_order", sale_order)
    #         for sale_order_line in sale_order.order_line:
    #             per  = per - sale_order_line.participation
    #         print("sale_order", sale_order)
    #         print("per", per)
    #         return int(per)
    #
    # participant_id = fields.Many2one(comodel_name="res.users", string="Utilisateur", tracking=True, default=lambda self: self.env.user)
    # participation = fields.Integer(string="Participation %", tracking=True, default=100)

    # attendees_ids = fields.One2many(comodel_name="sale.attendees", inverse_name="sale_order_line_id", string="Participants")
