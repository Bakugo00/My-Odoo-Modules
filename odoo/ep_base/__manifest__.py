# -*- coding: utf-8 -*-

{
    'name': 'Personnalisation de la Base',
    'version': '1.0',
    'description': """
         Personnalisation de la base pour l'entreprise Emploi Partner
   """,
    'category': 'Base',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['base','calendar', 'mail', 'contacts', 'product', 'account' , 'hr','sales_team','web_responsive','website','sale'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/security_calendar.xml',
        # views
        'views/menus.xml',
        'views/res_company_inherit.xml',
        'views/res_partner_inherit.xml',
        'views/company_type.xml',
        'views/company_state.xml',
        'views/company_status.xml',
        'views/email_phone_view.xml',
        'views/product_inherit.xml',
        'views/calendar_event_inherit.xml',
        'views/activity_result.xml',
        'views/activity_result_category.xml',
        'views/mail_activity_inherit.xml',
        'views/mail_message_views.xml',
        'views/calendar.xml',
        'views/res_users_inherit.xml',
        # data
        #    'data/company_data.xml',
        #    'data/product_category_data.xml',
        # reports
        'report/header_footer_template.xml',
        'report/header_footer_template_for_invoice.xml',
        'report/paperformat_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ep_base/static/src/css/activity_formatting.css',
        ],
        'web.assets_backend': [
            'ep_base/static/src/components/activity/activity.xml',
            'ep_base/static/src/components/filter_panel/calendar_filter_panel.js',
            'ep_base/static/src/css/activity_formatting.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'update_xml': [],
}
