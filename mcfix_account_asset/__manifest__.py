# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Company Fix Accounting Assets',
    'version': '1',
    'summary': 'Creu Blanca configuration',
    'author': 'Creu Blanca',
    'sequence': 30,
    'description': "",
    'category': 'Creu Blanca',
    'website': 'http://www.creublanca.es',
    'depends': ['mcfix_account', 'account_asset'],
    'data': [
        'views/account_asset_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
