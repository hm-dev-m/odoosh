# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    receivable_sequence_id = fields.Many2one('ir.sequence', 'Receivable Sequence',
        domain=[('code', '=', 'partner.auto.receivable')])
    customer_number_sequence_id = fields.Many2one('ir.sequence', 'Customer Number Sequence',
        domain=[('code', '=', 'partner.auto.customer.number')])
    payable_sequence_id = fields.Many2one('ir.sequence', 'Payable Sequence',
        domain=[('code', '=', 'partner.auto.payable')])
    supplier_number_sequence_id = fields.Many2one('ir.sequence', 'Supplier Number Sequence',
        domain=[('code', '=', 'partner.auto.supplier.number')])
    receivable_template_id = fields.Many2one('account.account', 'Receivable Account Template')
    payable_template_id = fields.Many2one('account.account', 'Payable Account Template',
        domain=[('type', '=', 'payable')])
    add_number_to_partner_number = fields.Boolean('Add Account Number to Partner Numbers')
    add_number_to_partner_ref = fields.Boolean('Add Customer or Supplier Number to Partner Reference')
    use_separate_partner_numbers = fields.Boolean('Use separate Customer- / Supplier-Numbers')
    use_separate_accounts = fields.Boolean('Use Separate Accounts')
