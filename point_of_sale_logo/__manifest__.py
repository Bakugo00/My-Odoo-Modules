# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
{
    'name': 'Point of Sale Logo',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "Logo For Every Point of Sale (Screen & Receipt)",
    'description': "This module helps you to set a logo for every POS"
                   "This will help you to identify the point of sale easily."
                   "You can also see this logo in pos screen and pos receipt.",
    'author': 'Bahaeddine',
    'company': 'Bahaeddine',
    'maintainer': "Bahaeddine",
    'depends': ['point_of_sale'],
    'data': ['views/pos_config_views.xml'],
    'assets': {
        'point_of_sale._assets_pos': [
            'point_of_sale_logo/static/src/xml/navbar_logo.xml',
            'point_of_sale_logo/static/src/xml/receipt_logo.xml'
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
