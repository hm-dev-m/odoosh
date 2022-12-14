# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Odoo Webhook',
    'version': '1.0',
    'summary': 'A user-defined HTTP callbacks',
    'category': 'Tools',
    'description': """
Webhooks(A user-defined HTTP callbacks) are a useful tool for apps that want to execute code after a specific event happens on an Odoo, for example, after a warehouse manager creates a new product, updates a stock quantity for existing products or sales manager confirm the quotation etc.

Instead of telling your app to make an API call every X number of minutes to check if a specific event has occured on an Odoo, you can register webhooks, which send an HTTP request from the Odoo telling your app that the event has occurred. This uses many less API requests overall, allowing you to build more robust apps, and update your app instantly after a webhook is received.

Webhook event data can be stored as JSON or XML, and is commonly used when:
===========================================================================

- Placing an order
- Changing a product's price
- Collecting data for data-warehousing
- Integrating your accounting software
- Filtering the order items and informing various shippers about the order
- Another, less-obvious, case for using webhooks is when you're dealing with data that isn't easily searchable through the Odoo API. For example, re-requesting an entire product catalog or order history would benefit from using webhooks since it requires a lot of API requests and takes a lot of time.

Think of it this way, if you would otherwise have to poll for a substantial amount of data, you should be using webhooks.

The Odoo Webhook endpoints can be used for a variety of purposes such as:
=========================================================================

- Get a Webhook list
- Get a Webhook counts
- Create a new Webhook
- Update an existing Webhook
- Delete a Webhook from the database

Check out our online docs http://odoo-webhook.readthedocs.io for a quick reference guide to use the odoo webhooks.
""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['base', 'web', 'base_automation', 'restapi'],
    'external_dependencies': {
            'python': ['requests_oauthlib']},
    'data': [
        'data/webhook_security.xml',
        'security/ir.model.access.csv',
        'views/webhook_view.xml',
        'views/job_view.xml',
        'data/webhook_data.xml',
        'views/webhook_menu.xml',
        'wizard/requeue_job_view.xml'
    ],
    'demo': [],
    'css': [],
    'qweb': [],
    'js': [],
    'test': [],
    'images': [
        'static/description/main_screen.png',
    ],
    'price': 125,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
