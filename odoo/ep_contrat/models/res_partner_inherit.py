from odoo import fields, models

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    customer_contract_count = fields.Integer(compute='compute_count_customer_contract')

    def compute_count_customer_contract(self):
        for record in self:
            record.customer_contract_count = self.env['customer.contract'].search_count(
                [('partner_id', '=', self.id)])

    def action_view_customer_contract(self):
        action = self.env['ir.actions.act_window']._for_xml_id('ep_contrat.customer_contract_action')
        action["domain"] = [("partner_id", "=",self.id)]
        return action