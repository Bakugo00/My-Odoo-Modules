# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation de RH',
    'version': '1.0',
    'description': """
        Personnalisation de RH pour l'entreprise Emploi Partner
   """,
    'category': 'RH',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['ep_base', 'hr_contract','hr_attendance','hr','hr_holidays','maintenance'],
    'data': [
        # views
        'security/security_employee.xml',
        'security/security_presences.xml',
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'views/hr_attendance.xml',
        'views/menu.xml',
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
