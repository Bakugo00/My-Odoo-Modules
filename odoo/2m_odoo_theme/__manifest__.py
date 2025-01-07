# -*- coding: utf-8 -*-

{
    "name": "2mnumerik Theme",
    "description": """Backend theme for Odoo 14.0 community edition.""",
    'version': '14.0.1.0.0',
    'author': 'Emploi Partner',
    'company': 'Emploi Partner',
    'maintainer': 'Emploi Partner',
    "website": "www.emploipartner.com",
    "category": "Themes/Backend",
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png',
    ],
    "depends": [
        # 'website',
        'portal',
        'web_responsive',
        'calendar', 'mail', 'contacts', 'sale',
        'purchase' , 'stock', 'account'
    ],
    "data": [
        'views/assets.xml',
        'views/login_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
