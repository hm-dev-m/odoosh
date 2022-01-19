# -*- coding: utf-8 -*-
{
    'name': 'Sumup Odoo Connector',
    'version': '14.0.1.7.2',
    'author': 'Designcomplex',
    'category': 'Point Of Sale',
    'price': 199.00,
    'currency': 'EUR',
    'license':'OPL-1',
    'images': ['static/description/main_screenshot.jpg'],
    'summary': 'Manage SumUp card reader through SumUp mobile application (iPadOS, iOS and Android) from Odoo POS front end',
    'description': """
    This module adds the possibility to use the SumUp App on iPadOS, iOS and Android for POS payment methods.
    The user will be redirected with to the SumUp app with all payment details and and the SumUp app will redirect back to Odoo after payment is completed or failed.
    Payment transactions details can be seen in Odoo on the POS ticket and in payment transaction journal entries in POS and finance modules.

    """,
    'category': 'Point Of Sale',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_sumup_lite.xml',         # JS binding
        'views/pos_sumup_lite_view.xml',
    ],
    'demo': [
        'data/pos_sumup_lite_demo.xml'
    ],
    'qweb': [
        'static/src/xml/pos_sumup_lite.xml'
    ],
    'installable': True,
    'auto_install': False,
}
