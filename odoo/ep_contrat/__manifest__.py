# -*- coding: utf-8 -*-

{
    'name' : 'Gestion des Contrats',
    'version' : '1.0',
    'description': """
         Gestion des contrats pour l'entreprise Emploi Partner
   """,
    'category': 'Contrat',
    'website': 'https://www.emploipartner.com',
    'images': [],
    'depends': ['base', 'mail' , 'account' , 'sale' , 'ep_base'],
    'data': [
        # data
          'data/contract_seq.xml',
          'data/cc_mail_template.xml',
          'data/ir_cron_data.xml',
         # security
          'security/contract_security.xml',
          'security/ir.model.access.csv',
         # # views
          'views/customer_contract_view.xml',
          'views/supplier_contract_view.xml',
          'views/contract_type_view.xml',
          'views/menus.xml',
          'views/sale_order_inherit.xml',
          'views/res_partner_inherit_views.xml',
         # report
    ],
    'demo': [
    ],
    'qweb': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
