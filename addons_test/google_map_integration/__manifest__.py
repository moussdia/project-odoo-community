# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# mobile:+91-9020735717

{
    'name': 'Google map integration in portal address page',
    'summary': 'Customer Portal',
    'sequence': '9000',
    'category': 'website',
    'license': 'AGPL-3',
    'version': '1.0',
    'author': 'shameemmuhammad992@gmail.com',
    'maintainer': 'shameemmuhammad992@gmail.com',
    'description': """
This module adds  google map integration in customer portal address page and help to get partner latitude and longitude from google map and also available search location in google map. """,
    'depends': ['portal','website_sale'],
    'data': [
        #'views/portal_assets.xml',
        'views/portal_templates.xml',
        'views/res_config_settings.xml',
        'views/website_templates.xml'
    
    ],
    
    'application': True,
    'bootstrap': True,
    'application': True,
    'currency': 'USD',
    'price':41.0,
    'images': ['static/description/icon.png']
}
