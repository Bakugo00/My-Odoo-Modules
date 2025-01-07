# -*- encoding: utf-8 -*-
{
    'name': 'Oxycode ordre de mission',
    'sequence': 0,
    'summary': "Mission order",
    'version': '1.0',
    'category': 'Human Resource',
    'summary': "This module allows you to perform mission orders for employees of your company",
    'author': "OxyCode",
    'website': '',
    'depends': ['hr','ep_rh'],
    'data': [
        'views/mission_order_date_view.xml',  
        'views/mission_order_view.xml',
        'views/mission_employee_view.xml',
        'views/mission_object_view.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/mission_order_report.xml'
        ],
    'installable': True,
    'application': False,
}