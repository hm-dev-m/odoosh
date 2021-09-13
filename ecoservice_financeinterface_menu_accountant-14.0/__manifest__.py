# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'Finance Interface Menu Accountant',
    'summary': 'Make the menu account_accountant (Enterprise module) compliant',
    'category': 'Accounting',
    'version': '14.0.1.0.0',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice',
    'website': 'https://ecoservice.de/shop/product/odoo-datev-export-53',
    # Dependencies
    'depends': [
        'account_accountant',

        'ecoservice_financeinterface_datev',  # eco/finance-interface
    ],
    # Data
    'data': [
        'views/menu.xml',
    ],
}
