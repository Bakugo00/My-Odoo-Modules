# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation de la Vente',
    'version': '1.0',
    'description': """
        Personnalisation de la vente pour l'entreprise Emploi Partner
   """,
    'category': 'Sale',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['sale', 'sale_management','ep_base', 'mail','sale_stock','sales_team','base'],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # reports
        'report/report_saleorder_inherit.xml',
        # views
        'views/sale_order_menu.xml',
        'views/sale_order_inherit.xml',
        'views/account_move_inherit.xml',
        'views/sale_order_search_view_inherit.xml',
        'views/negotiation_step.xml',
        'views/product_template_inherit.xml',
        'views/res_config_settings_inherit.xml',
        # wizard
    ],
    'demo': [

    ],
    'qweb': [
       'static/src/xml/activity_inherit.xml',
       # 'static/src/components/activity/activity.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
