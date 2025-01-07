# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation du CRM',
    'version': '1.0',
    'description': """
        Personnalisation du CRM pour l'entreprise Emploi Partner
   """,
    'category': 'CRM',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['crm' ,'ep_base', 'mail','base','hr_recruitment'],
    'data': [
        # data
        'data/sequence.xml',
        # security
        'security/security.xml',
        'security/securiy_crm.xml',
        'security/security_portfolio.xml',
        'security/security_objective.xml',
        'security/security_activity.xml',
        'security/ir.model.access.csv',
        # reports
        'report/contact_activity_report_views.xml',
        'report/contact_mail_message_report_views.xml',
        # views
        'views/portfolio.xml',
        'views/portfolio_category.xml',
        'views/res_partner_inherit.xml',
        'views/objective_type.xml',
        'views/objective.xml',
        'views/menus.xml',
        'views/crm_lead_inherit.xml',
        'views/crm_team_inherit.xml',
        'views/mail_activity.xml',
        'views/res_users_inherit.xml',
        'views/calendar_event_inherit.xml',
        # wizard
        'wizard/move_companies_wizard.xml'
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
