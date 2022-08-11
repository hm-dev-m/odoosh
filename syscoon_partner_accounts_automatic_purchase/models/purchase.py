#See LICENSE file for full copyright and licensing details.


from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        res = super(PurchaseOrder, self).create(vals) 
        partner = res.partner_id.commercial_partner_id
        if config.use_separate_partner_numbers:
            if 'purchase_order_supplier_numbers' in create_accounts: 
                types['supplier_number'] = True
        if types:
            self.env['res.partner'].create_accounts(partner, types) 
        return res    

    def button_confirm(self):
        config = self.env.company
        create_accounts = [auto.code for auto in config.create_auto_account_on]
        types = {}
        partner = self.partner_id.commercial_partner_id
        if 'purchase_order_supplier' in create_accounts:
            types['payable'] = True
        if config.use_separate_accounts:
            types['use_separate'] = True
        if config.add_number_to_partner_number:
            types['add_number'] = True        
        if types:
            self.env['res.partner'].create_accounts(partner, types) 
        return super(PurchaseOrder, self).button_confirm()

