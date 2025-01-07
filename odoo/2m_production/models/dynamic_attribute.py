from odoo import api, fields, models, _, tools

class OptionGroup(models.Model):
    _name = "group.option"

    name = fields.Char('Nom')
    option_ids = fields.One2many('option', 'group_id', string='Options')
    # product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=False, index=True)
    product_template_ids = fields.Many2many('product.template', string='Produits')

    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('filter_group'):
            if context.get('filter_group') == True:
                product = self.env['product.template'].browse(context['product_id'])
                args = [('id', 'in', product.dynamic_group_ids.ids)]

        return super(OptionGroup, self)._search(args, offset, limit, order, count=count, access_rights_uid=access_rights_uid)

class Option(models.Model):
    _name = "option"

    name = fields.Char('Nom')
    application = fields.Selection([
        ('plank', 'Sur la Planche'),('product', 'Sur le Produit fini')
    ], string='Application',required=True)
    group_id = fields.Many2one('group.option', string='group')
    value_ids = fields.One2many('option.value', 'option_id', string='value')

class OptionValue(models.Model):
    _name = "option.value"

    name = fields.Char('Nom')
    price = fields.Float('Prix')
    option_id = fields.Many2one('option', string='Option')

    def name_get(self):
        res = []
        for value in self:
            name = value.name
            if self._context.get('display_option'):
                name += ' : %s ' %  value.option_id.name
            res.append((value.id, name))
        return res

class OptionValue(models.Model):
    _name = "option.value.line"

    group_option_id = fields.Many2one('group.option', string='Group', required=True)
    option_id = fields.Many2one('option', string='Option',domain="[('group_id', '=', group_option_id)]", required=True)
    option_value_id = fields.Many2one('option.value', string='Valeur',domain="[('option_id', '=', option_id)]", required=True)
    price = fields.Float('Prix')
    dynamic_qty = fields.Boolean('Qté Dynamique',default=False)
    quantity = fields.Integer('Quantity',default=1)
    line_id = fields.Many2one('sale.order.line', string='line')
    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade', required=False, index=True)

    @api.onchange('option_value_id')
    def _onchange_option_value_id(self):
        for line in self:
            line.price = line.option_value_id.price