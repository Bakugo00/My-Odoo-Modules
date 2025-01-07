# -*- coding: utf-8 -*-

{
    'name': 'Timbre(1%)',
    'version': '1.0',
    'description': """
        Ajout de la taxe du timbre lors de paiement en espèces
   """,
    'author': 'EP Odoo Developers',
    'category': 'Sale',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['ep_vente','ep_facturation','l10n_dz'],
    'data': [
        'data/tax_data.xml',
        'views/sale_order_inherit.xml',
        'views/account_move_inherit.xml',
        'views/tax_view.xml',
        'views/account_payment_inherit.xml',
        'report/report_invoice_inherit.xml',
        'report/report_saleorder_inherit.xml',
        # wizard
        'wizard/account_payment_register_inherit.xml'
    ],

    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
