# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'syscoon Partner Debit and Credit Accounts',
    'version': '15.0.0.0.3',
    'author': 'syscoon Estonia OÜ',
    'license': 'OPL-1',
    'category': 'Accounting',
    'website': 'https://syscoon.com',
    'depends': [
        'base',
        'account'
    ],
    'description': """If a partner is created a new debit and/or credit account will be created following a 
    sequence that can be created individually per company.""",
    'data': [
        'data/partner_account_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner.xml',
        ],
    'active': False,
    'installable': True
}
