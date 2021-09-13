# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'Finance Interface',
    'summary': 'Base module of the Finance Interface',
    'category': 'Accounting',
    'version': '14.0.1.1.0',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://ecoservice.de/shop/product/odoo-datev-export-53',
    # Odoo Apps Store
    'price': 550.00,
    'currency': 'EUR',
    #'live_test_url': 'https://eco-finance-interface-14-0.test.ecoservice.de/',
    'support': 'financeinterface@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        'l10n_de',
    ],
    # Data
    'data': [
        'security/ecofi_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/account/account_move.xml',
        'views/account/account_move_line.xml',
        'views/ecofi/ecofi.xml',
        'views/ecofi/ecofi_validation.xml',
        'views/res/res_config_settings.xml',
        'wizards/export_ecofi.xml',

        'views/action.xml',  # references to wizards
        'views/menu.xml',
    ],
}
