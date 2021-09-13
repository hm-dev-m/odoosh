# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'Finance Interface DATEV',
    'summary': 'Export of account moves to DATEV',
    'category': 'Accounting',
    'version': '14.0.1.6.1',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://ecoservice.de/shop/product/odoo-datev-export-53',
    # Odoo Apps Store
    #'live_test_url': 'https://eco-finance-interface-14-0.test.ecoservice.de/',
    'support': 'financeinterface@ecoservice.de',
    'images': [
        'images/main_screenshot.png',
    ],
    # Dependencies
    'depends': [
        'ecoservice_financeinterface',  # eco/finance-interface
    ],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',

        # action used in res_config_view
        'wizards/views/ecofi_move_migration.xml',

        'views/account/account_account.xml',
        'views/account/account_move_line.xml',
        'views/account/account_tax.xml',
        'views/ecofi/ecofi.xml',
        'views/ecofi/ecofi_validation.xml',
        'views/res/res_config_settings.xml',
    ],
}
