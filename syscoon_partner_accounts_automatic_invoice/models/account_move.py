# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id', 'journal_id')
    def _check_account_created(self):
        accounts = False
        if self.partner_id and self.journal_id:
            if self.journal_id.type in ['sale', 'purchase']:
                journal_id = self.journal_id
                config = self.env.company
                create_accounts = [auto.code for auto in config.create_auto_account_on]
                types = {}
                partner = self.partner_id.commercial_partner_id
                if journal_id.type == 'sale':
                    partner_default_id = str(partner['property_account_receivable_id'].id)
                    if 'invoice_customer' in create_accounts:
                        types['receivable'] = True
                if journal_id.type == 'purchase':
                    partner_default_id = str(partner['property_account_payable_id'].id)
                    if 'invoice_supplier' in create_accounts:
                        types['payable'] = True
                if 'receivable' in types.keys() or 'payable' in types.keys():
                    if config.use_separate_accounts:
                        types['use_separate'] = True
                    if config.add_number_to_partner_number:
                        types['add_number'] = True
                if config.use_separate_partner_numbers:
                    if 'invoice_customer_numbers' in create_accounts and 'receivable' in types.keys():
                        types['customer_number'] = True
                    if 'invoice_supplier_numbers' in create_accounts and 'payable' in types.keys():
                        types['supplier_number'] = True
                if types:
                    accounts = self.env['res.partner'].create_accounts(partner, types)
                if self.line_ids and accounts:
                    for line in self.line_ids:
                        if journal_id.type == 'sale':
                            if self.partner_id and line.account_id.id == int(partner_default_id):
                                if accounts and accounts[2]:
                                    line.account_id = accounts[2].id
                        if journal_id.type == 'purchase':
                            if self.partner_id and line.account_id.id == int(partner_default_id):
                                if accounts and accounts[5]:
                                    line.account_id = accounts[5].id

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            accounts = False
            if val.get('move_type') and val['move_type'] in ['in_invoice', 'out_invoice', 'in_refund', 'out_refund'] and val.get('partner_id'):
                config = self.env.company
                create_accounts = [auto.code for auto in config.create_auto_account_on]
                types = {}
                partner = self.env['res.partner'].browse(val['partner_id'])
                partner = partner.commercial_partner_id
                if val['move_type'] in ['out_invoice', 'out_refund']:
                    partner_default_id = str(partner['property_account_receivable_id'].id)
                    if 'invoice_customer' in create_accounts:
                        types['receivable'] = True
                if val['move_type'] in ['in_invoice', 'in_refund']:
                    partner_default_id = str(partner['property_account_payable_id'].id)
                    if 'invoice_supplier' in create_accounts:
                        types['payable'] = True
                if 'receivable' in types.keys() or 'payable' in types.keys():
                    if config.use_separate_accounts:
                        types['use_separate'] = True
                    if config.add_number_to_partner_number:
                        types['add_number'] = True
                if config.use_separate_partner_numbers:
                    if 'invoice_customer_numbers' in create_accounts and 'receivable' in types.keys():
                        types['customer_number'] = True
                    if 'invoice_supplier_numbers' in create_accounts and 'payable' in types.keys():
                        types['supplier_number'] = True
                if types:
                    accounts = self.env['res.partner'].create_accounts(partner, types)
                if accounts:
                    if 'line_ids' in val and val['line_ids']:
                        for id in val['line_ids']:
                            if val['move_type'] in ['out_invoice', 'out_refund']:
                                if self.partner_id and id[2]['account_id'] == int(partner_default_id):
                                    if accounts and accounts[2]:
                                        id[2]['account_id'] = accounts[2].id
                            if val['move_type'] in ['out_invoice', 'out_refund']:
                                if self.partner_id and id[2]['account_id'] == int(partner_default_id):
                                    if accounts and accounts[5]:
                                        id[2]['account_id'] = accounts[5].id
        return super(AccountMove, self).create(vals_list)

