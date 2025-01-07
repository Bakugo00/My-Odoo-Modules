from odoo import api, fields, models, _
from odoo.tools import get_lang


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    # nbr_plank = fields.Integer(string="Nombre planches", store=True, default=0, compute='_compute_number_plank')
    # nbr_pro_per_plank = fields.Integer(string="Nombre poses", related='product_id.nbr_pro_per_plank', store=True,
    #                                    default=0)

    categ_id = fields.Many2one('product.category', related='product_template_id.categ_id', string="Catégorie produit")
    nbr_page = fields.Float('Nombre de page')
    price_page = fields.Float('Prix de page')
    nbr_insertion = fields.Float("Nombre d'insertion")
    price_insertion = fields.Float("Prix d'insertion")

    #Add these fields to use the composed product
    display_type = fields.Selection(selection_add=[('line_composed_product', 'Article Composé')])
    new_quantité = fields.Float('Quantité Unitaire',required=True, default=1)
    new_price_unit = fields.Float('Prix unitaire', compute='_compute_new_price_unit',store=True)
    parent_product = fields.Char('parent_product',compute='_compute_parent',store=True)

    @api.depends('order_id.order_line.price_unit')    
    def _compute_new_price_unit(self):
        for l in self:
            if l.display_type == 'line_composed_product':
                price = 0
                for line in sorted(l.order_id.order_line, key=lambda ln:ln.sequence):
                    if line.sequence > l.sequence:
                        if line.display_type == 'line_composed_product':
                            break
                        else:
                            price += line.prix_avec_remise * line.new_quantité
                l.new_price_unit = price
            else:
                l.new_price_unit = 0

    @api.depends('order_id.order_line.sequence','product_template_id')    
    def _compute_parent(self):
        for line in self:
            if line.display_type == 'line_composed_product':
                line.parent_product = line.product_template_id.name
            else:
                lines = line.order_id.order_line.filtered(lambda so_line : so_line.sequence < line.sequence and so_line.display_type =='line_composed_product')
                if lines:
                    composed_product_line = max(lines, key=lambda line: line.sequence)
                    line.parent_product = composed_product_line.name
                else:
                    line.parent_product = line.product_template_id.name


    # couverture = fields.Selection([('recto', 'Recto'), ('recto-verso', 'Recto-Verso')], string='Couverture',
    #                               default='recto')

    attribute_line_ids = fields.Many2many('product.template.attribute.line', string="Options" )
    dynamic_option_ids = fields.One2many('option.value.line', 'line_id', string='Options')

    @api.onchange('dynamic_option_ids')
    def _onchange_dynamic_option_ids(self):
        if self.dynamic_option_ids:
            name = self.product_template_id.name + '\n'
            for option in self.dynamic_option_ids:
                name += '   - %s:%s' % (option.option_id.name, option.option_value_id.name)
                name += '(%s)\n' % (option.quantity) if option.dynamic_qty else '\n'
            self.name = name

    def convert_to_meters(self, measure):
        uom_cmeters = self.env.ref("uom.product_uom_cm")
        uom_meters = self.env.ref("uom.product_uom_meter")
        return uom_cmeters._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False)
    
    dimension_id = fields.Many2one('dimension', string='Dimension')
    dim_height = fields.Float('Longueur')
    dim_width = fields.Float('Largeur')
    dimension_type = fields.Selection([
        ('standard', 'Standard'),('batard', 'Dynamique')
    ], string='Type de dimension',default='batard')
    nombre_de_pose = fields.Integer('Nombre de Poses', compute='_compute_nombre_de_pose',store=True)

    # @api.model
    # def _get_plank_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_plank").id)]
    
    # plank_id = fields.Many2one('product.template', string='Planche',readonly=False,domain=lambda self: self._get_plank_domain())
    product_to_consume = fields.Many2one('product.template', string='Article à Consommer')
    prix_avec_remise = fields.Float('Prix Avec remise',compute='_compute_prix_avec_remise')

    @api.depends('price_unit','discount')
    def _compute_prix_avec_remise(self):
        for line in self:
            line.prix_avec_remise = line.price_unit - (line.price_unit * line.discount / 100)

    @api.onchange('dimension_type')
    def _onchange_dimension_type(self):
        if self.dimension_type =='batard':
            self.dimension_id = False
            self.dim_height = 0.0
            self.dim_width = 0.0

    @api.onchange('dimension_id')
    def _onchange_dimension_id(self):
        if self.dimension_id:
            self.dim_height = self.dimension_id.height
            self.dim_width = self.dimension_id.width
        
    @api.depends('dim_height','dim_width','product_to_consume')  #'plank_id' 
    def _compute_nombre_de_pose(self):
        for line in self:
            nombre_de_pose = 0
            if line.product_template_id:
                plank = line.product_to_consume #plank_id
                if plank.has_dimension and plank.has_pince_spacing:
                    plank_length = self.convert_to_meters(plank.product_length)
                    plank_width = self.convert_to_meters(plank.product_width)
                    product_length = self.convert_to_meters(line.dim_height)
                    product_width = self.convert_to_meters(line.dim_width)
                    plank_pince = self.convert_to_meters(plank.pince)
                    plank_spacing = self.convert_to_meters(plank.spacing)
                    plank_length = plank_length - 2*plank_spacing
                    plank_width = plank_width - 2*plank_spacing
                    l_per_l = plank_length / (product_length + plank_pince) 
                    w_per_w = plank_width / (product_width + plank_pince)
                    nbr_pro_1 = int(l_per_l)* int(w_per_w) 
                    l_per_w = plank_length / (product_width + plank_pince) 
                    w_per_l = plank_width / (product_length + plank_pince) 
                    nbr_pro_2 = int(l_per_w)* int(w_per_l) 

                    # Final nbr_pro_per_plank
                    nombre_de_pose = max(nbr_pro_1,nbr_pro_2)
                    # # Fix the nb_pro_per_plank to 25 for product_category_card
                    # if nombre_de_pose > 25 and line.product_template_id.categ_id == self.env.ref(
                    #         "2m_production.product_category_card"):
                    if nombre_de_pose > 25 and line.product_template_id.categ_id.use_limit:
                        nombre_de_pose = line.product_template_id.categ_id.limit
            line.nombre_de_pose = nombre_de_pose

    @api.onchange('product_template_id')
    def fill_so_line_attribute_lines(self):
        for line in self:
            line.attribute_line_ids = [(5, 0, 0)]
            so_line_attributes = []
            for pro_attribute_line in line.product_template_id.attribute_line_ids:
                data_attribute_line = {}
                value_id = self.env['product.template.attribute.value'].search([('attribute_line_id', '=', pro_attribute_line.id),('name','=','Sans')])
                data_attribute_line.update({
                    'attribute_id': pro_attribute_line.attribute_id.id,
                    'template_value_id':value_id.id
                })

                so_line_attributes.append((0, 0, data_attribute_line))
            line.attribute_line_ids = so_line_attributes

    @api.onchange('attribute_line_ids','product_template_id')
    @api.depends('attribute_line_ids','product_template_id')
    def select_product_id(self):
        for line in self:
            product_ids = False
            if line.product_template_id and line.attribute_line_ids.template_value_id:
                product_ids = self.env['product.product'].search([('product_tmpl_id', '=', line.product_template_id.id)])
            elif line.product_template_id and not line.attribute_line_ids:
                line.product_id = self.env['product.product'].search([('product_tmpl_id', '=', line.product_template_id.id)])
            if product_ids and len(product_ids) >= 1:
                for pro in product_ids:
                    if pro.product_template_attribute_value_ids == line.attribute_line_ids.template_value_id:
                       line.product_id = pro

    # @api.model
    # def _get_couverture_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_couverture_brochure").id)]

    # couverture_id = fields.Many2one("product.product", string="Couverture",
    #                                 domain=lambda self: self._get_couverture_domain())

    # @api.model
    # def _get_roleaux_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_rouleaux").id)]

    # roleau_id = fields.Many2one("product.template", string="Rouleaux",
    #                             domain=lambda self: self._get_roleaux_domain())

    price_metre = fields.Monetary("Prix m²")
    product_length = fields.Float("Longueur Produit")
    product_width = fields.Float("Largeur Produit")

    # @api.depends('product_id', 'product_uom_qty')
    # @api.onchange('product_id', 'product_uom_qty')
    # def _compute_number_plank(self):
    #     """
    #      Compute the number of plank for the specific product and quntity
    #      @return:
    #        Number of plank needed
    #     """
    #     for line in self:
    #         nbr_plank = 0.0
    #         if line.product_id and line.product_id.plank_id:
    #             product = line.product_id
    #             if product.nbr_pro_per_plank != 0:
    #                 nbr_plank = line.product_uom_qty / product.nbr_pro_per_plank
    #                 # if the nbr_plank is not integer, add one plank to the total number of plank
    #                 nbr_plank = nbr_plank if nbr_plank.is_integer() else nbr_plank + 1
    #             line.nbr_plank = nbr_plank

    @api.onchange('categ_id', 'product_id', 'nbr_page', 'nbr_insertion',
                  'product_length', 'product_width','nombre_de_pose','order_id.partner_id','dynamic_option_ids','product_to_consume')
    @api.depends('categ_id', 'product_id',
                 'product_length', 'product_width')
    def compute_product_price(self):
        for so_line in self:
            if so_line.product_id:
                # if so_line.plank_id and so_line.categ_id != self.env.ref("2m_production.product_category_brochure"):
                if so_line.product_to_consume and so_line.product_id.categ_id.dimension == 'two':
                    base_price_plank = so_line.product_to_consume.list_price #plank_id
                    base_price_product = 0
                    final_price = 0
                    # for attribute in so_line.product_id.product_template_attribute_value_ids:
                    #     if attribute.application == 'plank':
                    #         base_price_plank += attribute.price_extra
                    #     else:
                    #         base_price_product += attribute.price_extra
                    for attribute in so_line.dynamic_option_ids:
                        if attribute.option_id.application == 'plank':
                            if attribute.dynamic_qty:
                                base_price_plank += attribute.price * attribute.quantity
                            else:
                                base_price_plank += attribute.price
                        else:
                            if attribute.dynamic_qty:
                                base_price_product += attribute.price * attribute.quantity
                            else:
                                base_price_product += attribute.price
                                
                    # the final price is computed with this formula :
                    # ( ( plank price + attributes plank price ) / Number of product per plank ) + attributes product price
                    nbr = (base_price_plank / so_line.nombre_de_pose) if so_line.nombre_de_pose != 0 else 0

                    # if so_line.categ_id == self.env.ref(
                    #         "2m_production.product_category_couverture_brochure") and so_line.product_id.couverture == 'recto':
                    #     nbr = nbr / 2

                    price = nbr + base_price_product
                    # if so_line.order_id.partner_id.customer_type == 'end_customer':
                    #     end_customer_price = price * (1 + so_line.product_id.margin / 100)
                    # else:
                    #     end_customer_price = price * (1 + so_line.product_id.margin_r / 100)

                # elif so_line.categ_id == self.env.ref("2m_production.product_category_bloc_note"):
                #     price = 0
                # elif so_line.categ_id == self.env.ref("2m_production.product_category_gf") and so_line.roleau_id:
                #     price = (so_line.product_width * so_line.product_length) * so_line.product_template_id.price_metre + \
                #             ((
                #                          so_line.roleau_id.product_width - so_line.product_width) * so_line.product_length) * so_line.roleau_id.list_price + so_line.product_id.price_extra

                # elif so_line.categ_id == self.env.ref("2m_production.product_category_papier_entete"):
                #     price = 0

                # elif so_line.categ_id == self.env.ref("2m_production.product_category_brochure"):
                #     #     # base_price_plank_couverture = so_line.product_id.plank_couverture.list_price
                #     #     # print("base_price_plank_couverture", base_price_plank_couverture)
                #     #     # base_price_plank = so_line.product_id.plank_id.list_price
                #     #     # base_price_product = 0
                #     #     # for attribute in so_line.product_id.product_template_attribute_value_ids:
                #     #     #     if attribute.application == 'plank':
                #     #     #         base_price_plank += attribute.price_extra
                #     #     #         base_price_plank_couverture += attribute.price_extra
                #     #     #     else:
                #     #     #         base_price_product += attribute.price_extra
                #     #     #
                #     #     # couverture_price = (base_price_plank_couverture / so_line.product_id.nbr_pro_per_plank) if so_line.product_id.nbr_pro_per_plank != 0 else 0
                #     #     # if so_line.couverture == 'recto':
                #     #     #     couverture_price = couverture_price / 2
                #     #     #
                #     #     # sous_price = ((base_price_plank / 4) * so_line.nbr_page) / so_line.product_id.nbr_pro_per_plank if so_line.product_id.nbr_pro_per_plank != 0 else 0
                #     #     # print("sous_price", sous_price)
                #     #     # print("couverture_price", couverture_price)
                #     #     # print("base_price_product", base_price_product)
                #     #
                #     couverture_price = so_line.couverture_id.lst_price
                #     base_price_plank = so_line.product_id.plank_id.list_price
                #     base_price_product = 0
                #     for attribute in so_line.product_id.product_template_attribute_value_ids:
                #         if attribute.application == 'plank':
                #             base_price_plank += attribute.price_extra
                #         else:
                #             base_price_product += attribute.price_extra

                #     sous_price = ((base_price_plank / 4) * so_line.nbr_page) / so_line.nombre_de_pose if so_line.nombre_de_pose != 0 else 0
                #     price = couverture_price + sous_price + base_price_product
                else :
                    price = so_line.product_id.lst_price
                if so_line.order_id.partner_id.customer_type == 'end_customer':
                    end_customer_price = price * (1 + so_line.product_id.margin / 100)
                else:
                    end_customer_price = price * (1 + so_line.product_id.margin_r / 100)
                so_line.price_unit = end_customer_price

    # Redefine this function to affect the lst_price to the sale_order_line
    # @api.depends('categ_id', 'nbr_page', 'nbr_insertion', 'price_page', 'price_insertion')
    # @api.onchange('categ_id', 'nbr_page', 'nbr_insertion', 'price_page', 'price_insertion')
    def _get_display_price(self, product):
        if self.order_id.partner_id.customer_type == "end_customer":
            return self.price_unit
        else:
            return self.price_unit
        return super()._get_display_price(product)
    
    @api.onchange('product_template_id')
    def calculer_la_remise(self):
        for line in self:
            Remise = self.env['remise'].search([('date_debut', '<=', line.order_id.date_order),('date_fin', '>=', line.order_id.date_order)], limit=1)
            if line.product_template_id in Remise.product_ids:
                line.discount = Remise.remise
            elif line.order_id.partner_id.categorie_client_id:
                line.discount = line.order_id.partner_id.categorie_client_id.remise
            else:
                line.discount = 0
    # @api.model
    # @api.onchange('product_id')
    # @api.depends('product_id')
    # def update_product_price(self):
    #     for line in self:
    #         line.price_unit = line.product_id.lst_price

    # @api.onchange('product_id')
    # def product_id_change(self):
    #     if not self.product_id:
    #         return
    #     valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
    #     # remove the is_custom values that don't belong to this template
    #     for pacv in self.product_custom_attribute_value_ids:
    #         if pacv.custom_product_template_attribute_value_id not in valid_values:
    #             self.product_custom_attribute_value_ids -= pacv
    #
    #     # remove the no_variant attributes that don't belong to this template
    #     for ptav in self.product_no_variant_attribute_value_ids:
    #         if ptav._origin not in valid_values:
    #             self.product_no_variant_attribute_value_ids -= ptav
    #
    #     vals = {}
    #     if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
    #         vals['product_uom'] = self.product_id.uom_id
    #         vals['product_uom_qty'] = self.product_uom_qty or 1.0
    #
    #     product = self.product_id.with_context(
    #         lang=get_lang(self.env, self.order_id.partner_id.lang).code,
    #         partner=self.order_id.partner_id,
    #         quantity=vals.get('product_uom_qty') or self.product_uom_qty,
    #         date=self.order_id.date_order,
    #         pricelist=self.order_id.pricelist_id.id,
    #         uom=self.product_uom.id
    #     )
    #
    #     vals.update(name=self.get_sale_order_line_multiline_description_sale(product))
    #
    #     self._compute_tax_id()
    #
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
    #         print("vals['price_unit']", vals['price_unit'])
    #         vals['price_unit'] = 100
    #         print("vals['price_unit']", vals['price_unit'])
    #
    #     self.update(vals)
    #
    #     title = False
    #     message = False
    #     result = {}
    #     warning = {}
    #     if product.sale_line_warn != 'no-message':
    #         title = _("Warning for %s", product.name)
    #         message = product.sale_line_warn_msg
    #         warning['title'] = title
    #         warning['message'] = message
    #         result = {'warning': warning}
    #         if product.sale_line_warn == 'block':
    #             self.product_id = False
    #
    #     return result

    # def _get_display_price(self, product):
    #     # TO DO: move me in master/saas-16 on sale.order
    #     # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
    #     # to be able to compute the full price
    #
    #     # it is possible that a no_variant attribute is still in a variant if
    #     # the type of the attribute has been changed after creation.
    #     no_variant_attributes_price_extra = [
    #         ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
    #             lambda ptav:
    #             ptav.price_extra and
    #             ptav not in product.product_template_attribute_value_ids
    #         )
    #     ]
    #     if no_variant_attributes_price_extra:
    #         product = product.with_context(
    #             no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
    #         )
    #
    #     if self.order_id.pricelist_id.discount_policy == 'with_discount':
    #         return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom.id).price
    #     product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)
    #
    #     final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
    #     base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
    #     final_price = 200
    #     base_price = 300
    #     print("final_price", final_price)
    #     print("base_price", base_price)
    #     if currency != self.order_id.pricelist_id.currency_id:
    #         base_price = currency._convert(
    #             base_price, self.order_id.pricelist_id.currency_id,
    #             self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
    #     # negative discounts (= surcharge) are included in the display price
    #     print("max(base_price, final_price)", max(base_price, final_price))
    #     print("-----------------")
    #     return max(base_price, final_price)

    # @api.onchange('product_uom', 'product_uom_qty')
    # def product_uom_change(self):
    #     if not self.product_uom or not self.product_id:
    #         self.price_unit = 0.0
    #         return
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         product = self.product_id.with_context(
    #             lang=self.order_id.partner_id.lang,
    #             partner=self.order_id.partner_id,
    #             quantity=self.product_uom_qty,
    #             date=self.order_id.date_order,
    #             pricelist=self.order_id.pricelist_id.id,
    #             uom=self.product_uom.id,
    #             fiscal_position=self.env.context.get('fiscal_position')
    #         )
    #         self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
    #
    #redefine this function to send values of both new_price_unit and new_quantity
    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'new_quantity' : self.new_quantité, 
            'new_price_unit' : self.new_price_unit,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id if not self.display_type else False,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res
