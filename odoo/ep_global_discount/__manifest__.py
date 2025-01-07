# -*- coding: utf-8 -*-

{
    'name': 'Remise Globale',
    'version': '1.0',
    'description': """
        Ajout de la remise globale dans les Devis et Factures
   """,
    'author': 'EP Odoo Developers',
    'category': 'Sale',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['ep_vente','ep_facturation'],
    'data': [
        'views/sale_order_inherit.xml',
        'views/account_move_inherit.xml',
        'report/report_invoice_inherit.xml',
        'report/report_saleorder_inherit.xml',

    ],
    'assets': {
    'web.assets_backend': [
        'ep_global_discount/static/src/js/hide_discount.js',
    ],
    },

    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
