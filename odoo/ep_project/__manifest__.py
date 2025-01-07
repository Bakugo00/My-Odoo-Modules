# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation du project',
    'version': '1.0',
    'description': """
        Personnalisation de Projet pour l'entreprise Emploi Partner
   """,
    'category': 'Project',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['project','web','hr_timesheet','base'],
    'data': [
        'data/ir_sequence_project_data.xml',
        "security/ir.model.access.csv",
        "security/security.xml",
        # views
        'views/project_views.xml',
        'views/timesheet_view.xml',
        'views/project_milestone_views.xml',
        'views/menus.xml',
    ],
    'demo': [

    ],
   'assets': {
        'web.assets_backend': [
            'ep_project/static/src/js/StateSelectionWidget.js',
            'ep_project/static/src/scss/StateSelectionWidget.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
