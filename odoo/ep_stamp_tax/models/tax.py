
from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = "account.tax.template"

    is_stamp = fields.Boolean("Est un Timbre")


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_stamp = fields.Boolean("Est un Timbre")
    min_value = fields.Float('Valeur Minimum', required=True, track_visibility='always')
    max_value = fields.Float('Plafond', required=True, track_visibility='always')

    @api.model
    def create(self, vals):
        tax = super(AccountTax, self).create(vals)
        if 'install_module' in self.env.context and self.env.context['install_module'] == 'ep_stamp_tax':
            if not 'duplicated_tax' in self.env.context:
                self.create_stamp_tax_for_companies()
        return tax

    #this function is added to duplicate the stamp tax
    @api.model
    def create_stamp_tax_for_companies(self):
        stamp_tax = self.search([('name','=','Timbre 1,0%')])
        if stamp_tax:
            companies = self.env['res.company'].search([])
            for company in companies:
                existing_tax = self.search([('name', '=', stamp_tax.name), ('company_id', '=', company.id)])
                if not existing_tax:
                    for line in stamp_tax.invoice_repartition_line_ids:
                        if line.repartition_type == 'tax' and line.account_id:
                            new_account_id = self.env['account.account'].search([('company_id','=',company.id),('name','=',line.account_id.name)])
                   
                    invoice_repartition_line_ids = [(5, 0, 0),
                                                (0, 0, {
                                                    'factor_percent': 100,
                                                    'repartition_type': 'base',
                                                }),
                                                (0, 0, {
                                                    'factor_percent': 100,
                                                    'repartition_type': 'tax',
                                                    'account_id': new_account_id.id,
                                                }),
                                                ]
                    refund_repartition_line_ids = [(5, 0, 0),
                                                (0, 0, {
                                                    'factor_percent': 100,
                                                    'repartition_type': 'base',
                                                }),
                                                (0, 0, {
                                                    'factor_percent': 100,
                                                    'repartition_type': 'tax',
                                                    'account_id': new_account_id.id,
                                                }),
                                                ]
                    stamp_tax.with_context({'duplicated_tax':True}).copy({'name':stamp_tax.name,'company_id': company.id,'refund_repartition_line_ids':refund_repartition_line_ids,
                                    'invoice_repartition_line_ids':invoice_repartition_line_ids}) 