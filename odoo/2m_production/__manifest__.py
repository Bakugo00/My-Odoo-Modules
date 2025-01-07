# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation de la Production',
    'version': '1.0',
    'description': """
         Personnalisation de la Production pour le client 2mnumerik
   """,
    'category': 'MRP',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['mrp',  'stock', 'purchase',
                'sale_product_configurator','sale_mrp' , 'product_expiry','ep_vente','ep_facturation','2m_odoo_theme'],
    'data': [
     # data
        'data/product_categ_data.xml',
        'data/mrp_data.xml',
        'data/email_template.xml',
     # security
        'security/security.xml',
        'security/ir.model.access.csv',
     # views
        'views/product_attribute_inherit.xml',
        'views/product_category_inherit.xml',
        'views/product_inherit.xml',
        'views/product_template_attribute_value_inherit.xml',
        'views/product_template_inherit.xml',
        'views/stock_picking_inherit.xml',
        'views/stock_inventory_inherit.xml',
        'views/stock_scrap_inherit.xml',
        'views/res_partner_inherit.xml',
        'views/mrp_production_inherit.xml',
        'views/mrp_workorder_inherit.xml',
        'views/mrp_unbuild_inherit.xml',
        'views/mrp_routing_workcenter_inherit.xml',
        'views/mrp_bom_inherit.xml',
        'views/sale_order_inherit.xml',
        'views/delivery_method.xml',
        'views/dimension.xml',
        'views/categorie_client.xml',
        'views/template.xml',
        'views/payment_view.xml',
        # 'views/sale_product_configuration_inherit.xml',
     # report
        'report/mrp_production_templates_inherit.xml',
        'report/sale_order_report.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
