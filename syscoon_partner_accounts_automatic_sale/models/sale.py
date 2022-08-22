#See LICENSE file for full copyright and licensing details.


from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        res = super(SaleOrder, self).create(vals) 
        partner = res.partner_id.commercial_partner_id
        if config.use_separate_partner_numbers:
            if 'sale_order_customer_numbers' in create_accounts: 
                types['customer_number'] = True
        if types:
            self.env['res.partner'].create_accounts(partner, types) 
        return res       

    def action_confirm(self):
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        partner = self.partner_id.commercial_partner_id
        if 'sale_order_customer' in create_accounts:
            types['receivable'] = True
        if config.use_separate_accounts:
            types['use_separate'] = True
        if config.add_number_to_partner_number:
            types['add_number'] = True
        if config.use_separate_partner_numbers:
            if 'sale_order_customer_numbers' in create_accounts: 
                types['customer_number'] = True      
        if types:
            self.env['res.partner'].create_accounts(partner, types) 
        return super(SaleOrder, self).action_confirm()

