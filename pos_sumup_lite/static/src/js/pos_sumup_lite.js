odoo.define('pos_sumup_lite.main', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var models = require('point_of_sale.models');
const PosComponent = require('point_of_sale.PosComponent');
const PaymentScreen = require('point_of_sale.PaymentScreen');
const PaymentScreenStatus = require('point_of_sale.PaymentScreenStatus');
const OrderWidget = require('point_of_sale.OrderWidget');
const ReceiptScreen = require('point_of_sale.ReceiptScreen');
const Registries = require('point_of_sale.Registries');
var pos_model = require('point_of_sale.models');
var utils = require('web.utils');
var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;
var round_pr = utils.round_precision;
var _t = core._t;
var _Order_proto = models.Order.prototype;

var deviceIsIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
var deviceIsAndroid = /Android/i.test(navigator.userAgent);

var is_sumup_transaction = false;
var add_sumup_payment_fees = false;
var sumup_widgets_ready = false;
var sumup_callback_url = window.location.protocol + '//' + window.location.host + '/pos/web/sumup_response';
var transactionTimer = null;


// Add fields to the POS model
pos_model.load_fields("pos.payment.method", [
    'use_sumup_mob_app_and_card_reader',
    'sumup_add_payment_fees',
    'sumup_payment_fees_percentage',
]);


models.Paymentline = models.Paymentline.extend({
    smp_tx_code: '',
});


const OrderWidgetSumup = (OrderWidget) =>
    class extends OrderWidget {
        
        _updateSummary() {
            if (this.order.sumup_payment_fees === 0.0) {
                super._updateSummary(...arguments);
            }
        }
        
    }; // const OrderWidgetSumup = (OrderWidget)
Registries.Component.extend(OrderWidget, OrderWidgetSumup);


// this._super() - don't work in models.Order!
models.Order = models.Order.extend({
    
    sumup_payment_fees: 0.0,
    
    get_total_with_tax: function() {
        var res = _Order_proto.get_total_with_tax.apply(this,arguments);
        if (this.sumup_payment_fees > 0) {
            res += this.sumup_payment_fees;
        }
        return round_pr(res, this.pos.currency.rounding);
    },
    
    
    export_as_JSON: function() {
        var res = _Order_proto.export_as_JSON.apply(this,arguments);
        res['transaction_code'] = this.selected_paymentline ? this.selected_paymentline.smp_tx_code : '';
        res['payment_fees'] = this.sumup_payment_fees;
        return res;
    },
    
}); // models.Order.extend


// Analog of 'click_back()' Odoo v13
PosComponent.prototype.showScreen = function(name, props) {
    
    // Added code (for 'Back' button):
    
    if (props !== undefined && name === 'ProductScreen') {
        
        if (is_sumup_transaction) {
            
            // Break SumUp transaction:
            if (transactionTimer) {
                // stop timer
                clearInterval(transactionTimer);
                transactionTimer = null;
            }
            
            // Remove current payment line
            var currentOrder = this.env.pos.get_order();
            currentOrder.remove_paymentline(currentOrder.selected_paymentline);
            
            currentOrder.sumup_payment_fees = 0.0;
            destroy_sumup_widgets(currentOrder);
            
        } // if (is_sumup_transaction)
        
    } // if (props !== undefined ...
    
    // Original function's code
    this.trigger('show-main-screen', { name, props });
    
} // PosComponent.prototype.showScreen() - Analog of 'click_back()' Odoo v13


const PaymentScreenSumup = (PaymentScreen) =>
    class extends PaymentScreen {
        
        addNewPaymentLine({ detail: paymentMethod }) {
            if (is_sumup_transaction) {
                return;
            }
            
            var res = super.addNewPaymentLine(...arguments);
            
            if (res && paymentMethod.use_sumup_mob_app_and_card_reader) {
                is_sumup_transaction = true;
                
                // Remove unnecessary payment lines:
                var currentLine = this.selectedPaymentLine;
                var lines_to_remove = [];
                for (let li of this.paymentLines) {
                    if (li !== currentLine) {
                        lines_to_remove.push(li.cid);
                    }
                }
                for (let li_to_rm of lines_to_remove) {
                    this.deletePaymentLine({ detail: { cid: li_to_rm } });
                }
                
                var dueTotal = this.currentOrder.get_total_with_tax();
                
                // Set payment fees parameters
                if (paymentMethod.sumup_add_payment_fees) {
                    add_sumup_payment_fees = true;
                    var fees_percentage = paymentMethod.sumup_payment_fees_percentage;
                    var fees_raw = dueTotal * fees_percentage / 100.0;
                    this.currentOrder.sumup_payment_fees = round_pr(fees_raw, this.env.pos.currency.rounding);
                }
                
                // Set current amount in the line
                if (add_sumup_payment_fees) {
                    dueTotal = this.currentOrder.get_total_with_tax();
                }
                this.selectedPaymentLine.set_amount(dueTotal);
                
                // Prepare SumUp widgets
                if (!sumup_widgets_ready) {
                    prepare_sumup_widgets();
                }
                
            } // if (res && paymentMethod.use_sumup_mob_app_and_card_reader)
            
            return res;
        } // addNewPaymentLine()
        
        
        // SumUp transaction button handler
        button_sumup_start_onclick() {
            
            // Break if exists active transaction
            if (transactionTimer) {
                return;
            }
            
            var dueTotal = this.currentOrder.get_total_with_tax();
            
            // Check for zero total sum
            if (!dueTotal) {
                this.showPopup('ErrorPopup',{
                    'title': _t('ERROR:'),
                    'body': _t('Zero total sum!'),
                });
                return;
            }
            
            // Check for non iOS/Android device:
            if (!deviceIsIOS && !deviceIsAndroid) {
                this.showPopup('ErrorPopup',{
                    'title': _t('ERROR:'),
                    'body': _t('This feature is only available on iOS/Android devices!'),
                });
                return;   // to comment for debug
            }
            
            // Disable (style) button itself
            $('.button.sumup_start').css('opacity', 0.5);
            
            // Hide payment fees
            if (add_sumup_payment_fees) {
                $('.sumup-label-payment-fees').addClass('oe_hidden');
            }
            
            // Hide the send receipt inputs
            $('.sumup-send-receipt-to-mobile').addClass('oe_hidden');
            $('.sumup-send-receipt-to-email').addClass('oe_hidden');
            
            // Show warning to wait for transaction finish
            $('.sumup-label-wait-for-finish').removeClass('oe_hidden');
            
            // Launch SumUp mobile application with parameters:
            
            var transactionUUID = generateUUID();
            // Debug:
//            alert('(DEBUG) transactionUUID:\n' + transactionUUID);
            
            var launch_uri = 'sumupmerchant://pay/1.0' +
                '?affiliate-key=' + this.env.pos.config.sumup_affiliate_key +
                '&amount=' + dueTotal +
                '&currency=' + this.env.pos.currency.name +
                '&title=' + "Odoo POS Payment: " + this.currentOrder.name +
                '&foreign-tx-id=' + transactionUUID;
            
            if (this.env.pos.config.sumup_app_id) {
                launch_uri += '&app-id=' + this.env.pos.config.sumup_app_id;
            }
            
            // Add receipt targets
            var send_receipt_to_mobile = $('#input_sumup_send_receipt_to_mobile').val();
            var send_receipt_to_email = $('#input_sumup_send_receipt_to_email').val();
            if (send_receipt_to_mobile) {
                launch_uri += '&receipt-mobilephone=' + send_receipt_to_mobile;
            }
            if (send_receipt_to_email) {
                launch_uri += '&receipt-email=' + send_receipt_to_email;
            }
            
            if (deviceIsIOS) {
                launch_uri += '' +
                    '&callbackfail=' + sumup_callback_url +
                    '&callbacksuccess=' + sumup_callback_url;
            } else if (deviceIsAndroid) {
                launch_uri += '' +
                    '&callback=' + sumup_callback_url;
            }
            
            // Launch SumUp mobile app
            window.open(launch_uri, 'SumUp');
            
//            // Debug:
//            var curr_paymentline = this.selectedPaymentLine;
//            curr_paymentline.smp_tx_code = 'XXXXXXXXX';
//            this.validateOrder(true);
//            is_sumup_transaction = false;
//            sumup_widgets_ready = false;
//            return;
            
            // Start SumUp transaction response callback:
            
            var checkInterval = this.env.pos.config.sumup_check_transaction_interval;
            var receivedTransactionResults = false;
            
            // SumUp transaction response callback:
            transactionTimer = setInterval(() => {
                
                // Check data in Odoo database
                rpc.query({
                        model: 'pos.sumup.transaction',
                        method: 'search_read',
                        args: [
                            [['uuid', '=', transactionUUID]],
                            ['successful', 'message', 'smp_tx_code'],
                        ],
                        limit: 1,
                    })
                    .then((transaction) => {
                        transaction = transaction[0]
                        if (transaction) {
                            if (!receivedTransactionResults) {
                                if (transaction.successful) {
                                    // Transaction successful:
                                    
                                    var curr_paymentline = this.selectedPaymentLine;
                                    curr_paymentline.smp_tx_code = transaction.smp_tx_code;
                                    
                                    // Validate order (with force validation)
                                    this.validateOrder(true);
                                    
                                    destroy_sumup_widgets(this.currentOrder);
                                    
                                } else {
                                    // Transaction fail:
                                    
                                    // Hide warning label
                                    $('.sumup-label-wait-for-finish').addClass('oe_hidden');
                                    // Show payment fees
                                    if (add_sumup_payment_fees) {
                                        $('.sumup-label-payment-fees').removeClass('oe_hidden');
                                    }
                                    // Show the send receipt inputs
                                    $('.sumup-send-receipt-to-mobile').removeClass('oe_hidden');
                                    $('.sumup-send-receipt-to-email').removeClass('oe_hidden');
                                    
                                    // Enable (style) button itself
                                    $('.button.sumup_start').css('opacity', 1);
                                    
                                    // Show popup message
                                    this.showPopup('ErrorPopup',{
                                        'title': _t('SumUp transaction FAIL:'),
                                        'body': _t(transaction.message),
                                    });
                                    
                                } // Transaction fail
                                
                                receivedTransactionResults = true;
                            }
                        }
                    });
                
                if (receivedTransactionResults) {
                    if (transactionTimer) {
                        // stop timer
                        clearInterval(transactionTimer);
                        transactionTimer = null;
                    }
                }
                
            }, checkInterval); // SumUp transaction response callback
            
        } // button_sumup_start_onclick() - SumUp transaction button handler
    
    }; // const PaymentScreenSumup = (PaymentScreen)
Registries.Component.extend(PaymentScreen, PaymentScreenSumup);


const PaymentScreenStatusSumup = (PaymentScreenStatus) =>
    class extends PaymentScreenStatus {
        
        constructor() {
            super(...arguments);
            // owl - Dictionary for UI state vals
            this.sumupUiState = {};
        }
        
        get currentOrder() {
            // Fill the send receipt inputs
            const client = this.env.pos.get_order().get_client();
            this.sumupUiState.inputMobile = (client && client.phone) || '';
            this.sumupUiState.inputEmail = (client && client.email) || '';
            
            return super.currentOrder;
        }
        
    }; // const PaymentScreenStatusSumup = (PaymentScreenStatus)
Registries.Component.extend(PaymentScreenStatus, PaymentScreenStatusSumup);


const ReceiptScreenSumup = (ReceiptScreen) =>
    class extends ReceiptScreen {
        
        constructor() {
            super(...arguments);
            // owl - Send value to screen
            this.is_sumup_transaction = is_sumup_transaction;
        }
        
    }; // const ReceiptScreenSumup = (ReceiptScreen)
Registries.Component.extend(ReceiptScreen, ReceiptScreenSumup);


function prepare_sumup_widgets() {
    
    // Show SumUp transaction button
    $('.button.sumup_start').removeClass('oe_hidden');
    $('.button.sumup_start').css('opacity', 1);
    
    // Hide unnecessary widgets
    $('.paymentlines').addClass('oe_hidden');
    $('.customer-button').addClass('oe_hidden');
    $('.button.js_invoice').addClass('oe_hidden');
    $('.button.js_tip').addClass('oe_hidden');
    $('.button.js_cashdrawer').addClass('oe_hidden');
    $('.button.next').addClass('oe_hidden');  // btn 'Validate' v1
    $('.btn-switchpane:first').addClass('oe_hidden');  // btn 'Validate' v2
    
    // Disable key press listener
    BarcodeEvents.stop();
    // Disable refresh-keys: F5 and Ctrl+R
    $('body').on('keydown', on_keydown_overrided);
    
    // Show payment fees
    if (add_sumup_payment_fees) {
        $('.sumup-label-payment-fees').removeClass('oe_hidden');
    }
    
    // Disable some widgets
    $('.paymentmethod').each(function(idx,el){
        el.disabled = true;     // this dont work (?) for 'owl' buttons with 'on-click' in XML
        el.style.opacity = 0.5;
    });
    // (numpad)
    $('.numpad .input-button').attr('disabled', true);
    $('.numpad .input-button').css('opacity', 0.5);
    $('.numpad .mode-button').attr('disabled', true);
    $('.numpad .mode-button').css('opacity', 0.5);
    
    sumup_widgets_ready = true;
    
} // function prepare_sumup_widgets()


function destroy_sumup_widgets(currentOrder) {
    
    is_sumup_transaction = false;
    sumup_widgets_ready = false;
    
    // Hide SumUp transaction button
    $('.button.sumup_start').addClass('oe_hidden');
    $('.button.sumup_start').css('opacity', 1);
    
    // Clear and hide payment fees
    if (add_sumup_payment_fees) {
        $('.sumup-label-payment-fees').addClass('oe_hidden');
        add_sumup_payment_fees = false;
    }
    
    // Enable widgets
    $('.paymentmethod').each(function(idx,el){
        el.disabled = false;    // this dont work (?) for 'owl' buttons with 'on-click' in XML
        el.style.opacity = 1;
    });
    // (numpad)
    $('.numpad .input-button').attr('disabled', false);
    $('.numpad .input-button').css('opacity', 1);
    $('.numpad .mode-button').attr('disabled', false);
    $('.numpad .mode-button').css('opacity', 1);
    
    // Widgets visibility
    $('.customer-button').removeClass('oe_hidden');
    $('.button.js_invoice').removeClass('oe_hidden');
    $('.button.js_tip').removeClass('oe_hidden');
    $('.button.js_cashdrawer').removeClass('oe_hidden');
    $('.button.next').removeClass('oe_hidden');  // btn 'Validate' v1
    $('.btn-switchpane:first').removeClass('oe_hidden');  // btn 'Validate' v2
    
    // Remove custom keyboard listener
    $('body').off('keydown', on_keydown_overrided);
    
    // Restore barcode listener
    BarcodeEvents.start();
    
} // function destroy_sumup_widgets()


function on_keydown_overrided(event) {
    // Block refresh-keys: F5 and Ctrl+R
    if (event.keyCode == 116 || (event.ctrlKey && event.keyCode == 82)) {
        event.stopPropagation();
        event.preventDefault();
        return false;
    }
} // function on_keydown_overrided()


function generateUUID() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
} // function generateUUID()

});
