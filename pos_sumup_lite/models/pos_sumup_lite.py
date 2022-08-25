# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    sumup_affiliate_key = fields.Char("Affiliate Key")
    sumup_app_id = fields.Char("App ID")
    sumup_check_transaction_interval = fields.Integer('Check Transaction Interval (milliseconds)', default=700)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    
    use_sumup_mob_app_and_card_reader = fields.Boolean('Use SumUp mobile application with SumUp card reader')
    sumup_add_payment_fees = fields.Boolean('Add payment fees')
    sumup_payment_fees_percentage = fields.Float(string='Payment fees percentage', digits=(7,3), default=0, required=True)
    sumup_default_customer_for_impersonal_orders = fields.Many2one('res.partner', 'Default customer for impersonal orders', help="In Odoo v15, when 'split_transactions==True', then 'Customer' is mandatory in PoS Orders.")


class PosSumupTransaction(models.Model):
    _name = 'pos.sumup.transaction'
    
    uuid = fields.Char('UUID', index=True, readonly=True)
    successful = fields.Boolean('Successful', readonly=True)
    message = fields.Text('Message', readonly=True)
    smp_tx_code = fields.Char('Smp-tx-code', readonly=True)


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    transaction_code = fields.Char('Transaction Code', readonly=True)
    payment_fees = fields.Float(string='Payment fees', digits='Account', readonly=True)
    ui_amount_total = fields.Float(string='uiTotal', store=True, digits=0, readonly=True)
    
    @api.onchange('payment_ids', 'lines')
    def _onchange_amount_all(self):
        super(PosOrder, self)._onchange_amount_all()
        for order in self:
            if order.ui_amount_total:
                order.amount_total = order.ui_amount_total
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['transaction_code'] = ui_order['transaction_code']
        res['payment_fees'] = ui_order['payment_fees']
        res['ui_amount_total'] = ui_order['amount_total']
        return res


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        res = super(PosSession, self)._get_split_receivable_vals(payment, amount, amount_converted)
        res['transaction_code'] = payment.pos_order_id.transaction_code
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _check_balanced(self):
        for move in self:
            # check for lines with 'transaction_code'
            if not move.line_ids.filtered(lambda l: l.transaction_code):
                super(AccountMove, move)._check_balanced()
        return True


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    transaction_code = fields.Char('Transaction Code', readonly=True)
