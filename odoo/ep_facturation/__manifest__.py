# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation de la Facturation',
    'version': '1.0',
    'description': """
       Personnalisation de la facturation pour l'entreprise Emploi Partner
   """,
    'category': 'Invoice',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['account', 'payment', 'sale', 'ep_base' , 'od_journal_sequence','l10n_dz','sale_stock','base','ep_crm'],
    'data': [
        # data
        'data/timbre_data.xml',
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/security_payment.xml',
        # views
        'views/account_move_inherit.xml',
        'views/product_template_inherit.xml',
        'views/account_move_search_view_inherit.xml',
        'views/recovery_step.xml',
        'views/res_partner_inherit.xml',
        'views/menus.xml',
        # 'views/timbre_view.xml',
        'views/account_payment_inherit.xml',
        'views/mail_activity.xml',
        # reports
        'report/report_invoice_inherit.xml',
        # wizard
        'wizard/account_payment_register_inherit.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
