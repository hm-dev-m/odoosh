# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{   'name': 'syscoon Financeinterface',
    'version': '15.0.0.0.7',
    'depends': ['account'],
    'author': 'syscoon Estonia OÜ',
    'license': 'OPL-1',
    'website': 'https://syscoon.com',
    'summary': 'Main Modul for export of accounting moves',
    'description': """The main modul syscoon_financeinterface provides the basic
        methods for finance exports to accounting software.""",
    'category': 'Accounting',
    'data': [
        'data/syscoon_financeinterface_sequence.xml',
        'reports/financeinterface_report.xml',
        'security/syscoon_financeinterface_security.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/syscoon_financeinterface.xml',
        'views/res_config_settings.xml',
        'wizards/syscoon_financeinterface_export.xml'
    ],
    'active': False,
    'installable': True
}
