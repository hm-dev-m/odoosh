# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_number = fields.Char(string='Customer Number', company_dependent=True)
    debitor_number = fields.Char(string='Debitor Number', company_dependent=True)
    supplier_number = fields.Char(string='Supplier Number', company_dependent=True)
    creditor_number = fields.Char(string='Creditor Number', company_dependent=True)

    def create_receivable_account(self):
        config = self.env.company
        partner = self
        types = {'receivable': True}
        if config.use_separate_accounts:
            types['use_separate'] = True
        if config.add_number_to_partner_number:
            types['add_number'] = True
        if config.use_separate_partner_numbers:
            types['customer_number'] = True
        return self.create_accounts(partner, types)

    def create_payable_account(self):
        config = self.env.company
        partner = self
        types = {'payable': True}
        if config.use_separate_accounts:
            types['use_separate'] = True
        if config.add_number_to_partner_number:
            types['add_number'] = True
        if config.use_separate_partner_numbers:
            types['supplier_number'] = True
        return self.create_accounts(partner, types)

    def create_customer_number(self):
        config = self.env.company
        partner = self
        types = {}
        if config.use_separate_partner_numbers:
            types['customer_number'] = True
        return self.create_accounts(partner, types)

    def create_supplier_number(self):
        config = self.env.company
        partner = self
        types = {}
        if config.use_separate_partner_numbers:
            types['supplier_number'] = True
        return self.create_accounts(partner, types)

    def create_accounts(self, partner, types={}):
        account_obj = self.env['account.account']
        values = {}
        if partner.parent_id:
            partner = partner.parent_id
        ref, debitor_number, customer_number, receivable_account_vals, creditor_number, \
            supplier_number, payable_account_vals = self.get_accounts(partner, types)
        receivable_account_id = payable_account_id = False
        if debitor_number:
            values['debitor_number'] = debitor_number
        if customer_number:
            values['customer_number'] = customer_number
        if receivable_account_vals:
            receivable_account_id = account_obj.sudo().create(receivable_account_vals)
            values['property_account_receivable_id'] = receivable_account_id.id
        if creditor_number:
            values['creditor_number'] = creditor_number
        if supplier_number:
            values['supplier_number'] = supplier_number
        if payable_account_vals:
            payable_account_id = account_obj.sudo().create(payable_account_vals)
            values['property_account_payable_id'] = payable_account_id.id
        if ref:
            values['ref'] = ref
        partner.write(values)
        return [debitor_number, customer_number, receivable_account_id, \
            creditor_number, supplier_number, payable_account_id]

    def get_accounts(self, partner, types={}):
        config = self.env.company
        debitor_number = creditor_number = customer_number = supplier_number = \
            receivable_account_vals = payable_account_vals = ref = False
        if partner.debitor_number:
            debitor_number = partner.debitor_number
        if partner.customer_number:
            customer_number = partner.customer_number
        if partner.creditor_number:
            creditor_number = partner.creditor_number
        if partner.supplier_number:
            supplier_number = partner.supplier_number
        if not debitor_number and 'receivable' in types.keys():
            debitor_number = config.receivable_sequence_id.next_by_id()
            if 'use_separate' in types.keys():
                receivable_field_ids = self.env['ir.model.fields'].search([
                    ('model', '=', 'res.partner'), 
                    ('name', '=', 'property_account_receivable_id')
                ])
                if len(receivable_field_ids) == 1:
                    receivable_account_vals = {
                        'name': partner.name,
                        'currency_id': config.receivable_template_id.currency_id and config.receivable_template_id.currency_id.id or False,
                        'code': debitor_number,
                        'user_type_id': config.receivable_template_id.user_type_id.id,
                        'reconcile': config.receivable_template_id.reconcile,
                        'tax_ids': [(6, 0, config.receivable_template_id.tax_ids.ids)],
                        'company_id': config.id,
                        'tag_ids': [(6, 0, config.receivable_template_id.tag_ids.ids)],
                        'group_id': config.receivable_template_id.group_id.id,
                    }
        if debitor_number and not customer_number and 'add_number' in types.keys():
            customer_number = debitor_number
        if not customer_number and 'customer_number' in types.keys():
            customer_number = config.customer_number_sequence_id.next_by_id()                 
        if not creditor_number and 'payable' in types.keys():
            creditor_number = config.payable_sequence_id.next_by_id()
            if 'use_separate' in types.keys():
                payable_field_ids = self.env['ir.model.fields'].search([
                    ('model', '=', 'res.partner'),
                    ('name', '=', 'property_account_payable_id')
                ])
                if len(payable_field_ids) == 1:
                    payable_account_vals = {
                        'name': partner.name,
                        'currency_id': config.payable_template_id.currency_id and config.payable_template_id.currency_id.id or False,
                        'code': creditor_number,
                        'user_type_id': config.payable_template_id.user_type_id.id,
                        'reconcile': config.payable_template_id.reconcile,
                        'tax_ids': [(6, 0, config.payable_template_id.tax_ids.ids)],
                        'company_id': config.id,
                        'tag_ids': [(6, 0, config.payable_template_id.tag_ids.ids)],
                        'group_id': config.payable_template_id.group_id.id,
                    }
        if creditor_number and not supplier_number and 'add_number' in types.keys():
            supplier_number = creditor_number
        if not supplier_number and 'supplier_number' in types.keys():
            supplier_number = config.supplier_number_sequence_id.next_by_id()
        if config.add_number_to_partner_ref and not self.ref:
            ref = customer_number or supplier_number
        return ref, debitor_number, customer_number, receivable_account_vals, creditor_number, supplier_number, payable_account_vals

