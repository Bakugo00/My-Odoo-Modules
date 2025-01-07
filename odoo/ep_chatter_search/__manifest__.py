# -*- coding: utf-8 -*-

{
    'name': 'Chatter Search',
    'version': '1.0',
    'description': """
        Ce module permet d'ajouter des fonctionnalités de recherche et de filtrage avancé dans le chatter d'Odoo.
        Il permet aux utilisateurs de rechercher des messages spécifiques et de filtrer les résultats par utilisateur et type d'activité.
   """,
    'category': 'Base',
    'website': 'www.emploipartner.com',
    'images': [],
    'depends': ['ep_base'],
    'data': [
        # security
        # views
    ],
    'assets': {
        'web.assets_backend': [
            'ep_chatter_search/static/src/components/chatter_topbar/chatter_topbar.esm.js',
            'ep_chatter_search/static/src/components/chatter_topbar/chatter_topbar.xml',
            'ep_chatter_search/static/src/components/chatter/chatter.esm.js',
            'ep_chatter_search/static/src/components/chatter/chatter.xml',
            'ep_chatter_search/static/src/components/chatter/chatter.css',
            'ep_chatter_search/static/src/components/activity/activity.xml',
            'ep_chatter_search/static/src/components/activity/activity.css',
            'ep_chatter_search/static/src/components/message/message.xml',
            'ep_chatter_search/static/src/components/message/message.css',
            'ep_chatter_search/static/src/components/thread/thread_cache.js',
            'ep_chatter_search/static/src/components/thread/thread.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'update_xml': [],
}
