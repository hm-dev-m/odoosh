# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create (self, vals):
        result = super(ResPartner, self).create(vals)
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        if result.commercial_partner_id.id == result.id:
            if self._context.get('default_customer_rank'):
                if 'partner_customer' in create_accounts:
                    types['receivable'] = True
            if self._context.get('default_supplier_rank'):
                if 'partner_supplier' in create_accounts:
                    types['payable'] = True
        if 'receivable' in types.keys() or 'payable' in types.keys():
            if config.use_separate_accounts:
                types['use_separate'] = True
            if config.add_number_to_partner_number:
                types['add_number'] = True
            if config.use_separate_partner_numbers:
                if 'partner_customer_numbers' in create_accounts and 'receivable' in types.keys():
                    types['customer_number'] = True
                if 'partner_supplier_numbers' in create_accounts and 'payable' in types.keys():
                    types['supplier_number'] = True
        if types:
            self.create_accounts(result, types)
        return result
