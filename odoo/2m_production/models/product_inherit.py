import itertools
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError


class ProductInherit(models.Model):
    _inherit = "product.product"
    _description = "Product"
    _inherits = {'product.template': 'product_tmpl_id'}
    _order = 'default_code, name, id'

    @api.model
    def _calc_volume(self, product_length, product_height, product_width, uom_id):
        volume = 0
        if product_length and product_height and product_width and uom_id:
            length_m = self.convert_to_meters(product_length, uom_id)
            height_m = self.convert_to_meters(product_height, uom_id)
            width_m = self.convert_to_meters(product_width, uom_id)
            volume = length_m * height_m * width_m

        return volume

    @api.onchange("product_length", "product_height", "product_width", "dimensional_uom_id")
    def onchange_calculate_volume(self):
        self.volume = self._calc_volume(
            self.product_length,
            self.product_height,
            self.product_width,
            self.dimensional_uom_id,
        )

    surface = fields.Float('Surface')

    couverture = fields.Selection([('recto', 'Recto'), ('recto-verso', 'Recto-Verso')], string='Couverture',
                                  default='recto')

    @api.model
    def _calc_surface(self, product_length, product_width):
        surface = 0
        if product_length and product_width :
            surface = product_length * product_width
        return surface

    @api.onchange("product_length", "product_width", "dimensional_uom_id")
    def onchange_calculate_surface(self):
        self.surface = self._calc_surface(
            self.product_length,
            self.product_height
        )

    def convert_to_meters(self, measure, dimensional_uom):
        uom_meters = self.env.ref("uom.product_uom_meter")
        return dimensional_uom._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    @api.model
    def _get_dimension_uom_domain(self):
        return [("category_id", "=", self.env.ref("uom.uom_categ_length").id)]

    product_length = fields.Float("Longueur")
    product_height = fields.Float("Hauteur")
    product_width = fields.Float("Largeur")
    dimensional_uom_id = fields.Many2one(
        "uom.uom",
        "Unité de mesure",
        domain=lambda self: self._get_dimension_uom_domain(),
        help="UoM for length, height, width",
        default=lambda self: self.env.ref("uom.product_uom_cm"),
        # default=lambda self: self.product_tmpl_id.dimensional_uom_id
    )

    pince = fields.Float('Prise pince', default=lambda self: self.product_tmpl_id.pince)
    spacing = fields.Float('Espacement', default=lambda self: self.product_tmpl_id.spacing)
    format = fields.Selection(string='Format', selection=[('small', 'Petit'), ('medium', 'Moyen'), ('big', 'Grand')])

    # margin = fields.Float(string="Marge Client")
    # end_customer_price = fields.Monetary(string="Prix client final", compute="_compute_end_customer_price")
    price_metre = fields.Monetary("Prix m²")

    # @api.depends('margin', 'lst_price')
    # def _compute_end_customer_price(self):
    #     """
    #      Compute the end_customer_price depending to the margin and the list_price
    #     """
    #     for product in self:
    #         product.end_customer_price = product.lst_price * (1 + product.margin / 100)

    # @api.model
    # def _get_plank_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_plank").id)]

    # plank_id = fields.Many2one("product.template", string="Planche",
    #                            domain=lambda self: self._get_plank_domain())

    # plank_couverture = fields.Many2one("product.template", string="Planche Couverture",
    #                                    domain=lambda self: self._get_plank_domain())

    # @api.model
    # def _get_structure_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_structure").id)]

    # structure_id = fields.Many2one("product.template", string="Structure",
    #                                domain=lambda self: self._get_structure_domain())

    # Hide the informations of the plank if the categ_id is not plank
    hide_plank_info = fields.Boolean(compute="_compute_hide_plank_info")

    has_dimension = fields.Boolean(compute='_compute_has_dimension', store=True)

    @api.depends('dimensional_uom_id', 'product_length', 'product_width')
    def _compute_has_dimension(self):
        for rec in self:
            rec.has_dimension = True if rec.dimensional_uom_id and rec.product_length != 0 and rec.product_width != 0 else False

    has_pince_spacing = fields.Boolean(compute='_compute_has_ps', store=True)

    @api.depends('pince', 'spacing')
    def _compute_has_ps(self):
        for rec in self:
            rec.has_pince_spacing = True if rec.pince != 0 and rec.spacing != 0 else False

    @api.depends('categ_id')
    def _compute_hide_plank_info(self):
        self.hide_plank_info = True if self.categ_id.dimension == 'two' else False

    # nbr_pro_per_plank = fields.Integer(string="Nombre de poses", compute='_compute_nbr_pro_per_plank',
    #                                    store=True, default=0)

    # @api.depends('plank_id', 'plank_id.product_length', 'plank_id.product_width', 'plank_id.pince', 'plank_id.spacing',
    #              'plank_id.dimensional_uom_id', 'product_length', 'product_width', 'dimensional_uom_id')
    # @api.onchange('plank_id', 'plank_id.product_length', 'plank_id.product_width', 'plank_id.pince', 'plank_id.spacing',
    #               'plank_id.dimensional_uom_id', 'product_length', 'product_width', 'dimensional_uom_id')
    # def _compute_nbr_pro_per_plank(self):
    #     """
    #      Compute the number of plank and the number of product per plank by dividing the plank surface into 4 zones
    #      Calculate the surfaces of each zone and the specific surface of the product
    #      Divide the surface of each zone on the specific surface of the product
    #      Get the nbr_product_per_plank
    #     @return:
    #        Number of product per plank
    #     """
    #     for product in self:
    #         nbr_pro_per_plank = 0.0
    #         if product.plank_id:
    #             plank = product.plank_id
    #             if product.has_dimension and plank.has_dimension and plank.has_pince_spacing:
    #                 plank_length = self.convert_to_meters(plank.product_length, plank.dimensional_uom_id)
    #                 plank_width = self.convert_to_meters(plank.product_width, plank.dimensional_uom_id)
    #                 product_length = self.convert_to_meters(product.product_length, product.dimensional_uom_id)
    #                 product_width = self.convert_to_meters(product.product_width, product.dimensional_uom_id)
    #                 plank_pince = self.convert_to_meters(plank.pince, plank.dimensional_uom_id)
    #                 plank_spacing = self.convert_to_meters(plank.spacing, plank.dimensional_uom_id)
    #                 # # Zone 1
    #                 # plank_surface = plank._calc_surface(plank_length - 2 * plank_pince - product_length,
    #                 #                                     plank_width - 2 * plank_pince - product_width)

    #                 # product_surface = product._calc_surface(product_length + plank_spacing,
    #                 #                                         product_width + plank_spacing)

    #                 # nbr_pro_per_plank = (plank_surface / product_surface) if product_surface != 0 else 0
    #                 # # Zone 2
    #                 # plank_surface = plank._calc_surface(product_width,
    #                 #                                     plank_width - 2 * plank_pince - product_width)

    #                 # product_surface = product._calc_surface(product_length,
    #                 #                                         product_width + plank_spacing)

    #                 # nbr_pro_per_plank += (plank_surface / product_surface) if product_surface != 0 else 0

    #                 # # Zone 3
    #                 # plank_surface = plank._calc_surface(plank_length - 2 * plank_pince - product_length,
    #                 #                                     product_width)

    #                 # product_surface = product._calc_surface(product_length + plank_spacing,
    #                 #                                         product_width)

    #                 # nbr_pro_per_plank += (plank_surface / product_surface) if product_surface != 0 else 0

    #                 # # Zone 4
    #                 # nbr_pro_per_plank += 1
    #                 # # Fix the nb_pro_per_plank to 25 for product_category_card
    #                 # if nbr_pro_per_plank > 25 and product.categ_id == self.env.ref(
    #                 #         "2m_production.product_category_card"):
    #                 #     nbr_pro_per_plank = 25
    #                 plank_length = plank_length - 2*plank_spacing
    #                 plank_width = plank_width - 2*plank_spacing
    #                 l_per_l = plank_length / (product_length + plank_pince) 
    #                 w_per_w = plank_width / (product_width + plank_pince)
    #                 nbr_pro_1 = int(l_per_l)* int(w_per_w) 
    #                 l_per_w = plank_length / (product_width + plank_pince) 
    #                 w_per_l = plank_width / (product_length + plank_pince) 
    #                 nbr_pro_2 = int(l_per_w)* int(w_per_l) 

    #                 # Final nbr_pro_per_plank
    #                 # product.nbr_pro_per_plank = int(nbr_pro_per_plank)
    #                 product.nbr_pro_per_plank = max(nbr_pro_1,nbr_pro_2)


    #                 # print("product.nbr_pro_per_plank",product.nbr_pro_per_plank)

    # @api.depends('list_price', 'price_extra', 'nbr_pro_per_plank', 'product_template_attribute_value_ids',
    #              'nbr_page', 'nbr_insertion', 'price_page', 'price_insertion', 'plank_id', 'structure_id', 'couverture')
    # @api.depends_context('uom')
    # def _compute_product_lst_price(self):
    #     # res = super(ProductInherit, self)._compute_product_lst_price()

    #     to_uom = None
    #     if 'uom' in self._context:
    #         to_uom = self.env['uom.uom'].browse(self._context['uom'])

    #     for product in self:
    #         if to_uom:
    #             list_price = product.uom_id._compute_price(product.list_price, to_uom)
    #         else:
    #             list_price = product.list_price
    #         product.lst_price = list_price + product.price_extra

    #         # Add this code to compute the lst_price of the variants
    #         if product.plank_id and product.categ_id != self.env.ref("2m_production.product_category_brochure"):
    #             base_price_plank = product.plank_id.list_price
    #             base_price_product = 0
    #             final_price = 0
    #             for attribute in product.product_template_attribute_value_ids:
    #                 if attribute.application == 'plank':
    #                     base_price_plank += attribute.price_extra
    #                 else:
    #                     base_price_product += attribute.price_extra
    #             # the final price is computed with this formula :
    #             # ( ( plank price + attributes plank price ) / Number of product per plank ) + attributes product price
    #             nbr = (base_price_plank / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0

    #             if product.categ_id == self.env.ref(
    #                     "2m_production.product_category_couverture_brochure") and product.couverture == 'recto':
    #                 nbr = nbr / 2

    #             final_price = nbr + base_price_product
    #             product.lst_price = final_price

            # Add this code to compute the lst_price of the variants when categ_id = banner
            # if product.structure_id:
            #     product.lst_price = product.structure_id.list_price + product.price_extra
            # Add this code to compute the lst_price of the variants when categ_id = bloc note
            # if product.categ_id == self.env.ref("2m_production.product_category_bloc_note"):
            #     product.lst_price = product.nbr_page * product.price_page + product.nbr_insertion * product.price_insertion + product.price_extra
            # # Add this code to compute the lst_price of the variants when categ_id = papier entete
            # if product.categ_id == self.env.ref("2m_production.product_category_papier_entete"):
            #     product.lst_price = product.price_page + product.price_extra
            # # Add this code to compute the lst_price of the variants when categ_id = brochure
            # if product.categ_id == self.env.ref("2m_production.product_category_brochure"):
            #     base_price_plank = product.plank_id.list_price
            #     base_price_product = 0
            #     final_price = 0
            #     for attribute in product.product_template_attribute_value_ids:
            #         if attribute.application == 'plank':
            #             base_price_plank += attribute.price_extra
            #         else:
            #             base_price_product += attribute.price_extra
            #     # the final price is computed with this formula :
            #     nbr = (((
            #                     base_price_plank / 4) * product.nbr_page) / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0
            #     final_price = nbr + base_price_product
            #     product.lst_price = final_price

    # def price_compute(self, price_type, uom=False, currency=False, company=None):
    #     # TDE FIXME: delegate to template or not ? fields are reencoded here ...
    #     # compatibility about context keys used a bit everywhere in the code
    #     if not uom and self._context.get('uom'):
    #         uom = self.env['uom.uom'].browse(self._context['uom'])
    #     if not currency and self._context.get('currency'):
    #         currency = self.env['res.currency'].browse(self._context['currency'])

    #     products = self
    #     if price_type == 'standard_price':
    #         # standard_price field can only be seen by users in base.group_user
    #         # Thus, in order to compute the sale price from the cost for users not in this group
    #         # We fetch the standard price as the superuser
    #         products = self.with_company(company or self.env.company).sudo()

    #     prices = dict.fromkeys(self.ids, 0.0)
    #     for product in products:
    #         prices[product.id] = product[price_type] or 0.0
    #         if price_type == 'list_price':

    #             prices[product.id] += product.price_extra
    #             # we need to add the price from the attributes that do not generate variants
    #             # (see field product.attribute create_variant)
    #             if self._context.get('no_variant_attributes_price_extra'):
    #                 # we have a list of price_extra that comes from the attribute values, we need to sum all that
    #                 prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

    #             # Add this code to compute the lst_price of the variants
    #             if product.plank_id and product.categ_id != self.env.ref("2m_production.product_category_brochure"):
    #                 base_price_plank = product.plank_id.list_price
    #                 base_price_product = 0
    #                 final_price = 0
    #                 for attribute in product.product_template_attribute_value_ids:
    #                     if attribute.application == 'plank':
    #                         base_price_plank += attribute.price_extra
    #                     else:
    #                         base_price_product += attribute.price_extra
    #                 # the final price is computed with this formula :
    #                 # ( ( plank price + attributes plank price ) / Number of product per plank ) + attributes product price
    #                 nbr = (base_price_plank / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0
    #                 if product.categ_id == self.env.ref(
    #                         "2m_production.product_category_couverture_brochure") and product.couverture == 'recto':
    #                     nbr = nbr / 2
    #                 final_price = nbr + base_price_product
    #                 # product.lst_price = final_price
    #                 prices[product.id] = final_price
    #             # Add this code to compute the lst_price of the variants
    #             # if product.structure_id:
    #             #     prices[product.id] = product.structure_id.list_price + product.price_extra
    #             # Add this code to compute the lst_price of the variants when categ_id = bloc note
    #             # if product.categ_id == self.env.ref("2m_production.product_category_bloc_note"):
    #             #     prices[
    #             #         product.id] = product.nbr_page * product.price_page + product.nbr_insertion * product.price_insertion + product.price_extra
    #             # # Add this code to compute the lst_price of the variants when categ_id = papier entete
    #             # if product.categ_id == self.env.ref("2m_production.product_category_papier_entete"):
    #             #     prices[product.id] = product.price_page + product.price_extra
    #             # # Add this code to compute the lst_price of the variants when categ_id = brochure
    #             # if product.categ_id == self.env.ref("2m_production.product_category_brochure"):
    #             #     base_price_plank = product.plank_id.list_price
    #             #     base_price_product = 0
    #             #     final_price = 0
    #             #     for attribute in product.product_template_attribute_value_ids:
    #             #         if attribute.application == 'plank':
    #             #             base_price_plank += attribute.price_extra
    #             #         else:
    #             #             base_price_product += attribute.price_extra
    #             #     # the final price is computed with this formula :
    #             #     nbr = (((
    #             #                         base_price_plank / 4) * product.nbr_page) / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0
    #             #     final_price = nbr + base_price_product
    #             #     prices[product.id] = final_price

    #     if uom:
    #         prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

    #         # Convert from current user company currency to asked one
    #         # This is right cause a field cannot be in more than one currency
    #     if currency:
    #         prices[product.id] = product.currency_id._convert(
    #             prices[product.id], currency, product.company_id, fields.Date.today())

    #     return prices
    #redefine this to remove () from the product variant name
    def name_get(self):
        # TDE: this could be cleaned a bit I think

        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = self._context.get('partner_id')
        if partner_id:
            partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        else:
            partner_ids = []
        company_id = self.env.context.get('company_id')

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights("read")
        self.check_access_rule("read")

        result = []

        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        if partner_ids:
            supplier_info = self.env['product.supplierinfo'].sudo().search([
                ('product_tmpl_id', 'in', product_template_ids),
                ('name', 'in', partner_ids),
            ])
            # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
            # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
            supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
            supplier_info_by_template = {}
            for r in supplier_info:
                supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        for product in self.sudo():
            variant = product.product_template_attribute_value_ids._get_combination_name()

            name = variant and "%s %s" % (product.name, variant) or product.name
            sellers = self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id')) or []
            if not sellers and partner_ids:
                product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
                sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
                if not sellers:
                    sellers = [x for x in product_supplier_info if not x.product_id]
                # Filter out sellers based on the company. This is done afterwards for a better
                # code readability. At this point, only a few sellers should remain, so it should
                # not be a performance issue.
                if company_id:
                    sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    temp = _name_get(mydict)
                    if temp not in result:
                        result.append(temp)
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result

    def _compute_product_price_extra(self):
        for product in self:
            product.price_extra = sum(product.product_template_attribute_value_ids.filtered(lambda att: att.application == 'product').mapped('price_extra'))

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, fields_list):
        res = super(ProductTemplateInherit, self).default_get(fields_list)
        taxes_id = self.env["account.tax"].search([('amount', 'in', (1, 19)), ('type_tax_use', '=', 'sale')])
        res.update({
            'taxes_id': taxes_id,
        })
        return res

    dynamic_group_ids = fields.Many2many('group.option', string='Options')
    # list_price: catalog price, user defined
    list_price = fields.Float(
        'Sales Price', default=0,
        digits='Product Price',
        help="Price at which the product is sold to customers.")

    type = fields.Selection([
        ('product', 'Article stockable'),
        ('consu', 'Consommations'),
        ('service', 'Service')], string="Type d'article", default='product', required=True)

    couverture = fields.Selection([('recto', 'Recto'), ('recto-verso', 'Recto-Verso')], string='Couverture',
                                  default='recto')

    @api.depends('categ_id')
    @api.onchange('categ_id')
    def default_route_ids(self):
        for product in self:
            if product.categ_id.category_policy == "buy":
                product.route_ids = [(6, 0, [self.env.ref("purchase_stock.route_warehouse0_buy").id])]
            elif product.categ_id.category_policy == "manufacture":
                product.route_ids = [(6, 0, [self.env.ref("stock.route_warehouse0_mto").id,
                                             self.env.ref("mrp.route_warehouse0_manufacture").id])]

    @api.model
    def _calc_volume(self, product_length, product_height, product_width, uom_id):
        volume = 0
        if product_length and product_height and product_width and uom_id:
            length_m = self.convert_to_meters(product_length, uom_id)
            height_m = self.convert_to_meters(product_height, uom_id)
            width_m = self.convert_to_meters(product_width, uom_id)
            volume = length_m * height_m * width_m

        return volume

    @api.onchange("product_length", "product_height", "product_width", "dimensional_uom_id")
    def onchange_calculate_volume(self):
        self.volume = self._calc_volume(
            self.product_length,
            self.product_height,
            self.product_width,
            self.dimensional_uom_id,
        )

    def convert_to_meters(self, measure, dimensional_uom):
        uom_meters = self.env.ref("uom.product_uom_meter")
        return dimensional_uom._compute_quantity(
            qty=measure,
            to_unit=uom_meters,
            round=False,
        )

    @api.model
    def _get_dimension_uom_domain(self):
        return [("category_id", "=", self.env.ref("uom.uom_categ_length").id)]

    product_length = fields.Float("Longueur")
    product_height = fields.Float("Hauteur")
    # product_height = fields.Float(
    #     related="product_variant_ids.product_height", readonly=False
    # )
    product_width = fields.Float("Largeur")
    dimensional_uom_id = fields.Many2one(
        "uom.uom",
        "Unité de mesure",
        domain=lambda self: self._get_dimension_uom_domain(),
        help="UoM for length, height, width",
        default=lambda self: self.env.ref("uom.product_uom_cm"),
    )

    pince = fields.Float('Prise pince')
    spacing = fields.Float('Espacement')
    format = fields.Selection(string='Format', selection=[('small', 'Petit'), ('medium', 'Moyen'), ('big', 'Grand')])

    # @api.model
    # def _get_plank_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_plank").id)]

    # plank_id = fields.Many2one("product.template", string="Planche",
    #                            domain=lambda self: self._get_plank_domain())

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('consume') and context.get('category'):
            categ= self.env["product.category"].search([('id','=',context.get('category'))]) 
            if categ:
                args = [('categ_id', '=',categ.categ_id.id)]
        return super(ProductTemplateInherit, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    # plank_couverture = fields.Many2one("product.template", string="Planche Couverture",
    #                                    domain=lambda self: self._get_plank_domain())

    # @api.model
    # def _get_structure_domain(self):
    #     return [("categ_id", "=", self.env.ref("2m_production.product_category_structure").id)]

    # structure_id = fields.Many2one("product.template", string="Structure",
    #                                domain=lambda self: self._get_structure_domain())

    # Hide the informations of the plank if the categ_id is not plank
    hide_plank_info = fields.Boolean(compute="_compute_hide_plank_info")
    price_metre = fields.Monetary("Prix m²")

    @api.depends('categ_id')
    def _compute_hide_plank_info(self):
        self.hide_plank_info = True if self.categ_id.dimension == 'two' else False

    has_dimension = fields.Boolean(compute='_compute_has_dimension', store=True)

    @api.depends('dimensional_uom_id', 'product_length', 'product_width')
    def _compute_has_dimension(self):
        for rec in self:
            rec.has_dimension = True if rec.dimensional_uom_id and rec.product_length != 0 and rec.product_width != 0 else False

    has_pince_spacing = fields.Boolean(compute='_compute_has_ps', store=True)

    @api.depends('pince', 'spacing')
    def _compute_has_ps(self):
        for rec in self:
            rec.has_pince_spacing = True if rec.pince != 0 and rec.spacing != 0 else False

    surface = fields.Float('Surface')

    @api.model
    def _calc_surface(self, product_length, product_width):
        surface = 0
        if product_length and product_width :
            surface = product_length * product_width
        return surface

    @api.onchange("product_length", "product_width", "dimensional_uom_id")
    def onchange_calculate_surface(self):
        self.surface = self._calc_surface(
            self.product_length,
            self.product_height
        )

    # nbr_pro_per_plank = fields.Integer(string="Nombre de poses", compute='_compute_nbr_pro_per_plank',
    #                                    store=True, default=0)

    margin = fields.Float(string="Marge client Final(%)")
    margin_r = fields.Float(string="Marge client Revendeur(%)")

    # end_customer_price = fields.Monetary(string="Prix client final", compute='_compute_end_customer_price')

    nbr_page = fields.Float('Nombre de page')
    price_page = fields.Float('Prix de page')

    nbr_insertion = fields.Float("Nombre d'insertion")
    price_insertion = fields.Float("Prix d'insertion")

    # @api.depends('margin', 'list_price')
    # def _compute_end_customer_price(self):
    #     """
    #      Compute the end_customer_price depending to the margin and the list_price
    #     """
    #     for product in self:
    #         product.end_customer_price = product.list_price * (1 + product.margin / 100)

    # @api.depends('plank_id', 'plank_id.product_length', 'plank_id.product_width', 'plank_id.pince', 'plank_id.spacing',
    #              'plank_id.dimensional_uom_id', 'product_length', 'product_width', 'dimensional_uom_id')
    # @api.onchange('plank_id', 'plank_id.product_length', 'plank_id.product_width', 'plank_id.pince', 'plank_id.spacing',
    #               'plank_id.dimensional_uom_id', 'product_length', 'product_width', 'dimensional_uom_id')
    # def _compute_nbr_pro_per_plank(self):
    #     """
    #      Compute the number of plank and the number of product per plank by dividing the plank surface into 4 zones
    #      Calculate the surfaces of each zone and the specific surface of the product
    #      Divide the surface of each zone on the specific surface of the product
    #      Get the nbr_product_per_plank
    #     @return:
    #        Number of product per plank
    #     """
    #     for product in self:
    #         nbr_pro_per_plank = 0.0
    #         if product.plank_id:
    #             plank = product.plank_id
    #             if product.has_dimension and plank.has_dimension and plank.has_pince_spacing:
    #                 plank_length = self.convert_to_meters(plank.product_length, plank.dimensional_uom_id)
    #                 plank_width = self.convert_to_meters(plank.product_width, plank.dimensional_uom_id)
    #                 product_length = self.convert_to_meters(product.product_length, product.dimensional_uom_id)
    #                 product_width = self.convert_to_meters(product.product_width, product.dimensional_uom_id)
    #                 plank_pince = self.convert_to_meters(plank.pince, plank.dimensional_uom_id)
    #                 plank_spacing = self.convert_to_meters(plank.spacing, plank.dimensional_uom_id)
    #                 # # Zone 1
    #                 # plank_surface = plank._calc_surface(plank_length - 2 * plank_pince - product_length,
    #                 #                                     plank_width - 2 * plank_pince - product_width)

    #                 # product_surface = product._calc_surface(product_length + plank_spacing,
    #                 #                                         product_width + plank_spacing)

    #                 # nbr_pro_per_plank = (plank_surface / product_surface) if product_surface != 0 else 0
    #                 # # Zone 2
    #                 # plank_surface = plank._calc_surface(product_width,
    #                 #                                     plank_width - 2 * plank_pince - product_width)

    #                 # product_surface = product._calc_surface(product_length,
    #                 #                                         product_width + plank_spacing)

    #                 # nbr_pro_per_plank += (plank_surface / product_surface) if product_surface != 0 else 0

    #                 # # Zone 3
    #                 # plank_surface = plank._calc_surface(plank_length - 2 * plank_pince - product_length,
    #                 #                                     product_width)

    #                 # product_surface = product._calc_surface(product_length + plank_spacing,
    #                 #                                         product_width)

    #                 # nbr_pro_per_plank += (plank_surface / product_surface) if product_surface != 0 else 0

    #                 # # Zone 4
    #                 # nbr_pro_per_plank += 1

    #                 # # Fix the nb_pro_per_plank to 25 for product_category_card
    #                 # if nbr_pro_per_plank > 25 and product.categ_id == self.env.ref(
    #                 #         "2m_production.product_category_card"):
    #                 #     nbr_pro_per_plank = 25
    #                 plank_length = plank_length - 2*plank_spacing
    #                 plank_width = plank_width - 2*plank_spacing
    #                 l_per_l = plank_length / (product_length + plank_pince) 
    #                 w_per_w = plank_width / (product_width + plank_pince)
    #                 nbr_pro_1 = int(l_per_l)* int(w_per_w) 
    #                 l_per_w = plank_length / (product_width + plank_pince) 
    #                 w_per_l = plank_width / (product_length + plank_pince) 
    #                 nbr_pro_2 = int(l_per_w)* int(w_per_l) 
    #                 # Final nbr_pro_per_plank
    #                 # product.nbr_pro_per_plank = int(nbr_pro_per_plank)
    #                 product.nbr_pro_per_plank = max(nbr_pro_1,nbr_pro_2)
    #                 # print("product.nbr_pro_per_plank",product.nbr_pro_per_plank)

    # @api.depends('plank_id', 'structure_id', 'nbr_page', 'nbr_insertion', 'price_page', 'price_insertion',
    #              'structure_id.list_price', 'plank_id.list_price', 'nbr_pro_per_plank', 'couverture')
    # @api.onchange('plank_id', 'structure_id', 'nbr_page', 'nbr_insertion', 'price_page', 'price_insertion',
    #               'structure_id.list_price', 'plank_id.list_price', 'nbr_pro_per_plank', 'couverture')
    # def _compute_product_list_price(self):
    #     """
    #        Calculate the list_price of the product_template when it has a plank_id
    #     """
    #     for product in self:
    #         if product.plank_id and product.categ_id != self.env.ref("2m_production.product_category_brochure"):
    #             base_price_plank = product.plank_id.list_price
    #             value = (base_price_plank / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0
    #             if product.categ_id == self.env.ref(
    #                     "2m_production.product_category_couverture_brochure") and product.couverture == 'recto':
    #                 value = value / 2
    #             product.update({'list_price': value})
            # if product.structure_id:
            #     value = product.structure_id.list_price
            #     product.update({'list_price': value})
            # Add this code to compute the lst_price of the variants when categ_id = bloc note
            # if product.categ_id == self.env.ref("2m_production.product_category_bloc_note"):
            #     value = product.nbr_page * product.price_page + product.nbr_insertion * product.price_insertion
            #     product.update({'list_price': value})
            # # Add this code to compute the lst_price of the variants when categ_id = papier entete
            # if product.categ_id == self.env.ref("2m_production.product_category_papier_entete"):
            #     value = product.price_page
            #     product.update({'list_price': value})
            # # Add this code to compute the lst_price of the variants when categ_id = brochure
            # if product.categ_id == self.env.ref("2m_production.product_category_brochure"):
            #     base_price_plank = product.plank_id.list_price
            #     value = (((
            #                           base_price_plank / 4) * product.nbr_page) / product.nbr_pro_per_plank) if product.nbr_pro_per_plank != 0 else 0
            #     product.update({'list_price': value})

    # Redefine this function to :
    # Affect dimensions ->  Line 437
    # Create the product without options -> Line 486
    # def _create_variant_ids(self):
    #     self.flush()
    #     Product = self.env["product.product"]

    #     variants_to_create = []
    #     variants_to_activate = Product
    #     variants_to_unlink = Product

    #     for tmpl_id in self:
    #         lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

    #         all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(
    #             lambda p: (p.active, -p.id))

    #         current_variants_to_create = []
    #         current_variants_to_activate = Product

    #         # adding an attribute with only one value should not recreate product
    #         # write this attribute on every product to make sure we don't lose them
    #         single_value_lines = lines_without_no_variants.filtered(
    #             lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1)
    #         if single_value_lines:
    #             for variant in all_variants:
    #                 combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
    #                 # Do not add single value if the resulting combination would
    #                 # be invalid anyway.
    #                 if (
    #                         len(combination) == len(lines_without_no_variants) and
    #                         combination.attribute_line_id == lines_without_no_variants
    #                 ):
    #                     variant.product_template_attribute_value_ids = combination

    #         # Set containing existing `product.template.attribute.value` combination
    #         existing_variants = {
    #             variant.product_template_attribute_value_ids: variant for variant in all_variants
    #         }

    #         # Determine which product variants need to be created based on the attribute
    #         # configuration. If any attribute is set to generate variants dynamically, skip the
    #         # process.
    #         # Technical note: if there is no attribute, a variant is still created because
    #         # 'not any([])' and 'set([]) not in set([])' are True.
    #         if not tmpl_id.has_dynamic_attributes():
    #             # Iterator containing all possible `product.template.attribute.value` combination
    #             # The iterator is used to avoid MemoryError in case of a huge number of combination.
    #             all_combinations = itertools.product(*[
    #                 ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
    #             ])
    #             # For each possible variant, create if it doesn't exist yet.
    #             for combination_tuple in all_combinations:
    #                 combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
    #                 if combination in existing_variants:
    #                     current_variants_to_activate += existing_variants[combination]
    #                 else:
    #                     #  Affect dimensions
    #                     product_length = tmpl_id.product_length
    #                     product_height = tmpl_id.product_height
    #                     product_width = tmpl_id.product_width
    #                     dimensional_uom_id = tmpl_id.dimensional_uom_id
    #                     for com in combination:
    #                         if com.product_attribute_value_id.is_dimension:
    #                             product_length = com.product_attribute_value_id.length
    #                             product_height = com.product_attribute_value_id.height
    #                             product_width = com.product_attribute_value_id.width
    #                             dimensional_uom_id = com.product_attribute_value_id.dimensional_uom_id
    #                     current_variants_to_create.append({
    #                         'product_tmpl_id': tmpl_id.id,
    #                         'product_template_attribute_value_ids': [(6, 0, combination.ids)],
    #                         'active': tmpl_id.active,
    #                         # Pass this fields to the variant :
    #                         'plank_id': tmpl_id.plank_id.id,
    #                         'couverture': tmpl_id.couverture,
    #                         # 'structure_id': tmpl_id.structure_id.id,
    #                         'nbr_page': tmpl_id.nbr_page,
    #                         'price_page': tmpl_id.price_page,
    #                         'nbr_insertion': tmpl_id.nbr_insertion,
    #                         'price_insertion': tmpl_id.price_insertion,
    #                         'product_length': product_length,
    #                         'product_height': product_height,
    #                         'product_width': product_width,
    #                         'dimensional_uom_id': dimensional_uom_id.id,
    #                         'margin': tmpl_id.margin,
    #                     })

    #                     if len(current_variants_to_create) > 100000:
    #                         raise UserError(_(
    #                             'The number of variants to generate is too high. '
    #                             'You should either not generate variants for each combination or generate them on demand from the sales order. '
    #                             'To do so, open the form view of attributes and change the mode of *Create Variants*.'))

    #             variants_to_create += current_variants_to_create
    #             variants_to_activate += current_variants_to_activate

    #         else:
    #             for variant in existing_variants.values():
    #                 is_combination_possible = self._is_combination_possible_by_config(
    #                     combination=variant.product_template_attribute_value_ids,
    #                     ignore_no_variant=True,
    #                 )
    #                 if is_combination_possible:
    #                     current_variants_to_activate += variant
    #             variants_to_activate += current_variants_to_activate

    #         variants_to_unlink += all_variants - current_variants_to_activate

    #     if variants_to_activate:
    #         variants_to_activate.write({'active': True})
    #     if variants_to_create:
    #         Product.create(variants_to_create)
    #     if variants_to_unlink:
    #         variants_to_unlink._unlink_or_archive()

    #     # Create the product without options
    #     if self.attribute_line_ids:
    #         # if not (len(self.attribute_line_ids) == 1 and ((len(attribute.value_ids) == 1) for attribute in self.attribute_line_ids )):
    #         vals = {
    #             'product_tmpl_id': self.id,
    #             'product_length': self.product_length,
    #             'product_height': self.product_height,
    #             'product_width': self.product_width,
    #             'dimensional_uom_id': self.dimensional_uom_id.id,
    #             'lst_price': self.list_price,
    #             'product_template_attribute_value_ids': [],
    #             'nbr_page': self.nbr_page,
    #             'price_page': self.price_page,
    #             'nbr_insertion': self.nbr_insertion,
    #             'price_insertion': self.price_insertion,
    #             'margin': self.margin,
    #         }
    #         if self.plank_id:
    #             vals.update({'plank_id': self.plank_id.id})
    #         if self.couverture:
    #             vals.update({'couverture': self.couverture})
    #         Product.create(vals)

    #     # prefetched o2m have to be reloaded (because of active_test)
    #     # (eg. product.template: product_variant_ids)
    #     # We can't rely on existing invalidate_cache because of the savepoint
    #     # in _unlink_or_archive.
    #     self.flush()
    #     self.invalidate_cache()
    #     return True
